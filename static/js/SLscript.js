document.addEventListener('DOMContentLoaded', () => {
    const wrap = document.getElementById("wrap");
    const body = document.body;
    let repeat = false;
    let playing = false;
    const audio = document.getElementById("audio");
    body.classList.add("album-1");

    gsap.registerPlugin(ScrollTrigger);

    ScrollTrigger.create({
        trigger: "#inner",
        start: "top 0%",
        end: "bottom 100%",
        scrub: "4",
        snap: {
            snapTo: 0.1,
            duration: { min: 0.3, max: 0.4 },
            delay: 0
        },
        onSnapComplete: (self) => {
            body.classList.add("album-" + (11 - Math.round(self.progress * 10)));
        },
        onUpdate: (self) => {
            body.className = '';
            playing = false;
            audio.pause();
            body.className = "";
            body.style.setProperty("--progress", self.progress);
            body.style.setProperty("--direction", self.direction);

            self.direction === -1 ? (repeat = true) : (repeat = false);

            if (self.progress === 1) {
                document.body.scrollTop = document.documentElement.scrollTop = 0;
            }
            if (self.progress === 0 && repeat && self.progress !== 1) {
                document.body.scrollTop = document.documentElement.scrollTop = wrap.scrollHeight;
                body.classList.add("album-1");
            }
        }
    });

    document.querySelectorAll(".album").forEach((album, index) => {
        const previewUrl = album.getAttribute('data-preview-url');
        album.addEventListener("mouseover", function () {
            if (!playing && previewUrl) {
                audio.setAttribute("src", previewUrl);
            }
        });
        album.addEventListener("click", function () {
            body.classList.toggle("bg-" + index);
            if (!playing) {
                setTimeout(() => {
                    audio.play();
                }, 1000);
            } else {
                audio.pause();
            }
            playing = !playing;
        });
    });
});
