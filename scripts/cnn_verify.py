import onnxruntime as ort, numpy as np, time, json, pathlib
model = pathlib.Path(r'G:\dad fucken around\tetris again\tetris_cnn.onnx')
sess = ort.InferenceSession(str(model))
input_meta = sess.get_inputs()[0]
shape = []
for dim in input_meta.shape:
    if isinstance(dim, int) and dim > 0:
        shape.append(dim)
    else:
        shape.append(1)
dummy = np.zeros(tuple(shape), dtype=np.float32)
inp = {input_meta.name: dummy}
t0 = time.time()
_ = sess.run(None, inp)
lat = (time.time() - t0) * 1000.0
print(f'Inference latency: {lat:.2f} ms')
with open('cnn_latency.json','w') as f:
    json.dump({'latency_ms': lat, 'input_shape': shape}, f)
