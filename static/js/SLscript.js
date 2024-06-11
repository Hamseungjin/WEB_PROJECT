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
      document.body.scrollTop = document.documentElement.scrollTop =
        wrap.scrollHeight;
      body.classList.add("album-1");
    }
  }
});

// Splitting.js 라이브러리 로드 확인
Splitting();

// DOM이 완전히 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {
  let playing = false;
  const body = document.body;
  const albums = document.querySelectorAll('.album');

  // 각 album 요소를 순회
  albums.forEach(function(album, index) {

    // 각 앨범의 오디오 요소 선택
    const audio = album.querySelector('#audio');
    const previewUrl = audio.getAttribute('data-preview-url');

    // 각 앨범의 텍스트 요소 선택 및 동적 텍스트 추가
    const textWrap = album.querySelector(".text");
    const trackName = album.getAttribute('data-track-name');
    const artistName = album.getAttribute('data-artist-name');
    textWrap.innerHTML += `<span>${trackName} • ${artistName} • </span>`;
     // Splitting.js 적용
    Splitting();
    // 각 앨범의 sleeve 요소 선택 및 이미지 URL 설정
    const sleeve = album.querySelector('.sleeve');
    const imageUrl = sleeve.getAttribute('data-image-url');
    sleeve.style.setProperty('--bg', `url(${imageUrl})`);
    Splitting();

    // 마우스 오버 이벤트 처리
    album.addEventListener('mouseover', function () {
      if (!playing) {
        audio.setAttribute('src', previewUrl);
      }
    });

    // 클릭 이벤트 처리
    album.addEventListener('click', function () {
      body.classList.toggle(`bg-${index}`);

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
