"""
Statistics Service - Centralized statistics collection and management.
Provides a clean API for match lifecycle, frame recording, and data aggregation.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from sqlmodel import Session, select, func
from .db import engine, get_session, Match, FrameEvent
from .collector import start_new_match, end_current_match, record_event

@dataclass
class MatchStats:
    """Statistics summary for a match."""
    match_id: int
    start_time: datetime
    end_time: Optional[datetime]
    total_frames: int
    pieces_placed: int
    lines_cleared: int
    max_combo: int
    total_b2b: int
    avg_fps: float
    piece_distribution: Dict[str, int]

@dataclass
class FrameStats:
    """Statistics for a single frame."""
    frame_number: int
    piece_type: str
    rotation: int
    position: tuple
    is_tspin: bool
    is_b2b: bool
    combo: int
    score: int
    timestamp: datetime

class StatsService:
    """Centralized statistics collection and analysis service."""
    
    def __init__(self):
        self._current_match_id: Optional[int] = None
        self._frame_counter: int = 0
        self._previous_piece: Optional[str] = None
        self._current_combo: int = 0
        self._b2b_counter: int = 0
        self.logger = logging.getLogger(__name__)
        
    def start_match(self) -> int:
        """Start a new match and return the match ID."""
        match_id = start_new_match()
        self._current_match_id = match_id
        self._frame_counter = 0
        self._current_combo = 0
        self._b2b_counter = 0
        self._previous_piece = None
        self.logger.info(f"Started new match with ID: {match_id}")
        return match_id
        
    def end_match(self) -> Optional[MatchStats]:
        """End the current match and return statistics summary."""
        if self._current_match_id is None:
            self.logger.warning("No active match to end")
            return None
            
        end_current_match()
        stats = self.get_match_stats(self._current_match_id)
        
        self.logger.info(f"Ended match {self._current_match_id}: "
                        f"{stats.total_frames} frames, {stats.pieces_placed} pieces")
        
        self._current_match_id = None
        return stats
        
    def record_frame(self, board_state: Any, piece_type: str, rotation: int, 
                    position: tuple, score: int, is_tspin: bool = False, 
                    is_b2b: bool = False) -> None:
        """Record a frame event with automatic combo/B2B detection."""
        if self._current_match_id is None:
            self.logger.warning("Cannot record frame - no active match")
            return
            
        self._frame_counter += 1
        
        # Auto-detect combo (piece change indicates placement)
        if self._previous_piece and self._previous_piece != piece_type:
            self._current_combo += 1
        else:
            self._current_combo = 0
            
        # Auto-detect B2B (consecutive difficult clears)
        if is_b2b:
            self._b2b_counter += 1
        else:
            self._b2b_counter = 0
            
        # Record the frame event
        record_event(
            match_id=self._current_match_id,
            frame_number=self._frame_counter,
            piece_type=piece_type,
            rotation=rotation,
            position=position,
            is_tspin=is_tspin,
            is_b2b=self._b2b_counter > 0,  # Use our counter
            combo=self._current_combo,
            score=score
        )
        
        self._previous_piece = piece_type
        
    def get_match_stats(self, match_id: int) -> Optional[MatchStats]:
        """Get comprehensive statistics for a specific match."""
        with get_session() as session:
            # Get match info
            match = session.get(Match, match_id)
            if not match:
                return None
                
            # Get frame events
            frames = session.exec(
                select(FrameEvent).where(FrameEvent.match_id == match_id)
                .order_by(FrameEvent.frame_number)
            ).all()
            
            if not frames:
                return MatchStats(
                    match_id=match_id,
                    start_time=match.start_time,
                    end_time=match.end_time,
                    total_frames=0,
                    pieces_placed=0,
                    lines_cleared=0,
                    max_combo=0,
                    total_b2b=0,
                    avg_fps=30.0,
                    piece_distribution={}
                )
            
            # Calculate statistics
            total_frames = len(frames)
            pieces_placed = len(set(f.piece_type for f in frames))
            max_combo = max((f.combo for f in frames), default=0)
            total_b2b = sum(1 for f in frames if f.is_b2b)
            
            # Piece distribution
            piece_counts = {}
            for frame in frames:
                piece_counts[frame.piece_type] = piece_counts.get(frame.piece_type, 0) + 1
            
            # Average FPS (estimated from timestamps)
            if len(frames) > 1:
                time_span = (frames[-1].timestamp - frames[0].timestamp).total_seconds()
                avg_fps = total_frames / time_span if time_span > 0 else 30.0
            else:
                avg_fps = 30.0
                
            return MatchStats(
                match_id=match_id,
                start_time=match.start_time,
                end_time=match.end_time,
                total_frames=total_frames,
                pieces_placed=pieces_placed,
                lines_cleared=0,  # Would need board analysis to calculate
                max_combo=max_combo,
                total_b2b=total_b2b,
                avg_fps=avg_fps,
                piece_distribution=piece_counts
            )
            
    def get_all_matches(self) -> List[MatchStats]:
        """Get statistics for all matches."""
        with get_session() as session:
            matches = session.exec(select(Match).order_by(Match.start_time.desc())).all()
            return [self.get_match_stats(match.id) for match in matches if match.id]
            
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics across all matches."""
        with get_session() as session:
            # Total matches
            total_matches = session.exec(select(func.count(Match.id))).one()
            
            # Total frames
            total_frames = session.exec(select(func.count(FrameEvent.id))).one()
            
            # Average FPS across all matches
            avg_fps_result = session.exec(
                select(func.avg(FrameEvent.timestamp))
            ).first()
            
            # Most common piece
            piece_stats = session.exec(
                select(FrameEvent.piece_type, func.count(FrameEvent.id))
                .group_by(FrameEvent.piece_type)
                .order_by(func.count(FrameEvent.id).desc())
            ).first()
            
            return {
                'total_matches': total_matches,
                'total_frames': total_frames,
                'most_common_piece': piece_stats[0] if piece_stats else 'N/A',
                'piece_frequency': piece_stats[1] if piece_stats else 0,
                'avg_fps': 30.0  # Would need more complex calculation
            }
            
    def export_match_data(self, match_id: int, format: str = 'json') -> str:
        """Export match data in specified format."""
        stats = self.get_match_stats(match_id)
        if not stats:
            return ""
            
        if format.lower() == 'json':
            import json
            return json.dumps({
                'match_id': stats.match_id,
                'start_time': stats.start_time.isoformat(),
                'end_time': stats.end_time.isoformat() if stats.end_time else None,
                'total_frames': stats.total_frames,
                'pieces_placed': stats.pieces_placed,
                'max_combo': stats.max_combo,
                'total_b2b': stats.total_b2b,
                'avg_fps': stats.avg_fps,
                'piece_distribution': stats.piece_distribution
            }, indent=2)
            
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['match_id', 'start_time', 'end_time', 'total_frames', 
                           'pieces_placed', 'max_combo', 'total_b2b', 'avg_fps'])
            
            # Data
            writer.writerow([
                stats.match_id,
                stats.start_time.isoformat(),
                stats.end_time.isoformat() if stats.end_time else '',
                stats.total_frames,
                stats.pieces_placed,
                stats.max_combo,
                stats.total_b2b,
                f"{stats.avg_fps:.2f}"
            ])
            
            return output.getvalue()
            
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    def cleanup_old_matches(self, days_to_keep: int = 30) -> int:
        """Clean up matches older than specified days."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with get_session() as session:
            # Delete old frame events
            deleted_frames = session.exec(
                select(FrameEvent).where(FrameEvent.timestamp < cutoff_date)
            ).delete()
            
            # Delete old matches
            deleted_matches = session.exec(
                select(Match).where(Match.start_time < cutoff_date)
            ).delete()
            
            session.commit()
            
            self.logger.info(f"Cleaned up {deleted_matches} matches and {deleted_frames} frames")
            return deleted_matches

# Global service instance
stats_service = StatsService()
