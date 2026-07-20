import { slides } from "./slides.js";
import { renderSlide } from "./renderer.js";

const presentation = document.querySelector("#presentation");
const previousButton = document.querySelector("#previous-button");
const nextButton = document.querySelector("#next-button");
const counter = document.querySelector("#slide-counter");
let currentSlide = 0;

function updatePresentation() {
  renderSlide(presentation, slides[currentSlide]);
  previousButton.disabled = currentSlide === 0;
  nextButton.disabled = currentSlide === slides.length - 1;
  counter.textContent = `${currentSlide + 1} / ${slides.length}`;
}

function move(direction) {
  const target = currentSlide + direction;
  if (target < 0 || target >= slides.length) return;
  currentSlide = target;
  updatePresentation();
}

previousButton.addEventListener("click", () => move(-1));
nextButton.addEventListener("click", () => move(1));

document.addEventListener("keydown", (event) => {
  if (["ArrowRight", " ", "PageDown"].includes(event.key)) {
    event.preventDefault();
    move(1);
  }
  if (["ArrowLeft", "PageUp"].includes(event.key)) {
    event.preventDefault();
    move(-1);
  }
  if (event.key === "Home") { currentSlide = 0; updatePresentation(); }
  if (event.key === "End") { currentSlide = slides.length - 1; updatePresentation(); }
});

updatePresentation();
