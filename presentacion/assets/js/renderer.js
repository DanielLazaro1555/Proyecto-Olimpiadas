export function renderSlide(container, slide) {
  container.innerHTML = `
    <section class="slide" tabindex="-1">
      <header>
        <p class="slide__eyebrow">${slide.eyebrow}</p>
        <h1 class="slide__title">${slide.title}</h1>
      </header>
      <div class="slide__body">${slide.content}</div>
    </section>`;

  container.querySelector(".slide").focus({ preventScroll: true });
}
