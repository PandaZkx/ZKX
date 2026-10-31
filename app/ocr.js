// Lecture des noms de héros sur une capture de la fenêtre du jeu (OCR local, rien n'est envoyé ni enregistré).
const path = require('path');
const { nativeImage } = require('electron');
let worker = null;
async function getWorker(cacheDir){
  if (worker) return worker;
  const { createWorker } = require('tesseract.js');
  worker = await createWorker('fra', 1, { langPath: path.join(__dirname, 'node_modules', '@tesseract.js-data', 'fra', '4.0.0'), gzip: true, cachePath: cacheDir });
  await worker.setParameters({ tessedit_pageseg_mode: '11' });
  return worker;
}
// garde le texte blanc (les noms), tout le reste devient blanc ; agrandi x2
function prep(img, rx, ry, rw, rh){
  const { width: W, height: H } = img.getSize(), src = img.toBitmap(), S = 2;
  const x0 = Math.round(W * rx), y0 = Math.round(H * ry), w = Math.round(W * rw), h = Math.round(H * rh);
  const out = Buffer.alloc(w * S * h * S * 4);
  for (let y = 0; y < h * S; y++) for (let x = 0; x < w * S; x++){
    const i = ((y0 + (y / S | 0)) * W + (x0 + (x / S | 0))) * 4, a = src[i], b = src[i + 1], c = src[i + 2];
    const mn = Math.min(a, b, c), white = mn > 185 && Math.max(a, b, c) - mn < 60, o = (y * w * S + x) * 4, v = white ? 0 : 255;
    out[o] = out[o + 1] = out[o + 2] = v; out[o + 3] = 255;
  }
  return nativeImage.createFromBitmap(out, { width: w * S, height: h * S }).toPNG();
}
function signature(img){ return img.resize({ width: 40, height: 24 }).toBitmap().filter((_, i) => i % 4 === 1).map(v => v >> 4).join(''); }
async function readFrame(img, cacheDir){
  const w = await getWorker(cacheDir);
  const list = (await w.recognize(prep(img, .795, .2, .13, .68))).data.text;
  const title = (await w.recognize(prep(img, .03, .02, .27, .12))).data.text;
  const name = (await w.recognize(prep(img, .01, .15, .3, .12))).data.text;
  return { list, title: title + '\n' + name };
}
async function stop(){ if (worker){ const w = worker; worker = null; await w.terminate().catch(() => {}); } }
module.exports = { readFrame, signature, stop };
