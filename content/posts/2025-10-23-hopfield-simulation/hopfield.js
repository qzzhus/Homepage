// Adapted from the Hopfield demo in ref/2025-1023 MC Simulation-Local Webpage.
// The heat-bath rule and incremental pattern-overlap calculation are preserved.
(() => {
  const demo = document.querySelector(".hopfield-demo");
  if (!demo) return;

  class Hopfield {
    constructor(N, T, patterns) {
      this.T = T;
      this.resize(N, patterns);
    }

    resize(N, patterns) {
      this.N = N;
      this.patterns = patterns;
      this.K = patterns.length;
      this.Spin = new Int8Array(N);
      for (let i = 0; i < N; i++) {
        this.Spin[i] = Math.random() < 0.5 ? 1 : -1;
      }
      this.overlaps = new Float64Array(this.K);
      this.calculate_all_overlaps();
    }

    calculate_all_overlaps() {
      for (let k = 0; k < this.K; k++) {
        let overlap = 0;
        for (let i = 0; i < this.N; i++) {
          overlap += this.patterns[k][i] * this.Spin[i];
        }
        this.overlaps[k] = overlap;
      }
    }

    heat_bath() {
      for (let n = 0; n < this.N; n++) {
        this.single_flip(Math.floor(Math.random() * this.N));
      }
    }

    single_flip(i) {
      const oldSpin = this.Spin[i];
      let localField = 0;
      for (let k = 0; k < this.K; k++) {
        const patternSpin = this.patterns[k][i];
        const overlapWithoutSelf = this.overlaps[k] - patternSpin * oldSpin;
        localField += patternSpin * overlapWithoutSelf / this.N;
      }
      const probability = 1 / (1 + Math.exp(2 * oldSpin * localField / this.T));
      if (Math.random() < probability) {
        this.Spin[i] = -oldSpin;
        for (let k = 0; k < this.K; k++) {
          this.overlaps[k] -= 2 * oldSpin * this.patterns[k][i];
        }
      }
    }
  }

  const size = 256;
  const canvas = demo.querySelector("canvas");
  const context = canvas.getContext("2d");
  const pixels = context.createImageData(size, size);
  const slider = demo.querySelector("#hopfield-temperature");
  const temperatureValue = demo.querySelector("#hopfield-temperature-value");
  const pauseButton = demo.querySelector("#hopfield-pause");
  const stepButton = demo.querySelector("#hopfield-step");
  const randomizeButton = demo.querySelector("#hopfield-randomize");
  const overlapValues = [...demo.querySelectorAll("[data-overlap]")];
  const sweepsValue = demo.querySelector("#hopfield-sweeps");
  const status = demo.querySelector("#hopfield-status");
  let model;
  let running = true;
  let sweeps = 0;
  let lastFrame = 0;
  let colors;

  function updateColors() {
    const style = getComputedStyle(demo);
    colors = ["--hopfield-spin-down", "--hopfield-spin-up"].map(name => {
      const hex = style.getPropertyValue(name).trim().replace("#", "");
      return [0, 2, 4].map(offset => parseInt(hex.slice(offset, offset + 2), 16));
    });
    if (model) draw();
  }

  function draw() {
    for (let i = 0; i < model.N; i++) {
      const color = colors[model.Spin[i] > 0 ? 1 : 0];
      const offset = i * 4;
      pixels.data[offset] = color[0];
      pixels.data[offset + 1] = color[1];
      pixels.data[offset + 2] = color[2];
      pixels.data[offset + 3] = 255;
    }
    context.putImageData(pixels, 0, 0);
  }

  function updateMetrics() {
    overlapValues.forEach((output, k) => {
      output.textContent = (model.overlaps[k] / model.N).toFixed(3);
    });
    sweepsValue.textContent = sweeps;
  }

  function step() {
    model.heat_bath();
    sweeps += 1;
    draw();
    updateMetrics();
  }

  function setRunning(value) {
    running = value;
    pauseButton.textContent = value ? "Pause" : "Resume";
    status.textContent = value ? "Running · heat-bath updates" : "Paused";
  }

  function animate(timestamp) {
    if (running && !document.hidden && timestamp - lastFrame >= 50) {
      lastFrame = timestamp;
      step();
    }
    requestAnimationFrame(animate);
  }

  slider.addEventListener("input", () => {
    temperatureValue.textContent = Number(slider.value).toFixed(2);
    if (model) model.T = Number(slider.value);
  });
  pauseButton.addEventListener("click", () => setRunning(!running));
  stepButton.addEventListener("click", () => {
    setRunning(false);
    step();
  });
  randomizeButton.addEventListener("click", () => {
    model.resize(model.N, model.patterns);
    sweeps = 0;
    draw();
    updateMetrics();
  });

  updateColors();
  new MutationObserver(updateColors).observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });

  async function loadPattern(url) {
    const image = new Image();
    image.src = url;
    await image.decode();
    const patternCanvas = document.createElement("canvas");
    patternCanvas.width = size;
    patternCanvas.height = size;
    const patternContext = patternCanvas.getContext("2d");
    patternContext.drawImage(image, 0, 0, size, size);
    const data = patternContext.getImageData(0, 0, size, size).data;
    const pattern = new Int8Array(size * size);
    for (let i = 0; i < pattern.length; i++) {
      const brightness = (data[4 * i] + data[4 * i + 1] + data[4 * i + 2]) / 3;
      pattern[i] = brightness < 128 ? -1 : 1;
    }
    return pattern;
  }

  async function init() {
    try {
      const urls = JSON.parse(demo.dataset.patterns);
      const patterns = await Promise.all(urls.map(loadPattern));
      model = new Hopfield(size * size, Number(slider.value), patterns);
      draw();
      updateMetrics();
      [pauseButton, stepButton, randomizeButton].forEach(button => {
        button.disabled = false;
      });
      setRunning(true);
      requestAnimationFrame(animate);
    } catch (error) {
      console.error("Hopfield simulation failed to initialize:", error);
      status.textContent = "The stored patterns could not load. Reload the page to try again.";
    }
  }
  init();
})();
