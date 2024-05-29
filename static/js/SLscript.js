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

const albums = {
  albums: [
    {
      artist: "R.M.F.C.",
      title: "Club‎ Hits",
      img: "https://f4.bcbits.com/img/a2827906655_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/RMFC.mp3"
    },
    {
      artist: "Tee‎ Vee‎ Repairmann",
      title: "What's on TV?",
      img: "https://f4.bcbits.com/img/a2866387299_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/TeeVee.mp3"
    },
    {
      artist: "Jeff‎ Rosenstock",
      title: "HELLMODE",
      img: "https://f4.bcbits.com/img/a0462955102_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/Rosenstock.mp3"
    },
    {
      artist: "King‎ Gizzard‎ &‎ the‎ Lizard‎ Wizard",
      title: "Petrodragonic‎ Apocalypse",
      img: "https://f4.bcbits.com/img/a2805471381_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/KingGizzard.mp3"
    },
    {
      artist: "The‎ Tubs",
      title: "Dead‎ Meat",
      img: "https://f4.bcbits.com/img/a1956044997_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/TheTubs.mp3"
    },
    {
      artist: "Prison‎ Affair",
      title: "Demo 3",
      img: "https://f4.bcbits.com/img/a1393633343_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/PrisonAffair.mp3"
    },
    {
      artist: "Home‎ Front",
      title: "Games‎ of‎ Power",
      img: "https://f4.bcbits.com/img/a1413020669_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/HomeFront.mp3"
    },
    {
      artist: "Billy‎ Woods‎ &‎ Kenny‎ Segal",
      title: "Maps",
      img: "https://f4.bcbits.com/img/a2712863742_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/BillyWoods.mp3"
    },
    {
      artist: "Mammatus",
      title: "Expanding‎ Majesty",
      img: "https://f4.bcbits.com/img/a3736762335_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/Mammatus.mp3"
    },
    {
      artist: "Snõõper",
      title: "Super‎ Snõõper",
      img: "https://f4.bcbits.com/img/a0289894971_16.jpg",
      audio: "https://github.com/adamjkuhn/audiofiles/raw/main/Snooper.mp3"
    },
  ]
};





document.querySelectorAll(".sleeve").forEach((album, index) => {
  body.style.setProperty(
    "--bg-" + index,
    "url(" + albums.albums[index].img + ")"
  );
  let textWrap = document.getElementsByClassName("text")[index];
  textWrap.innerHTML +=
    "<span data-splitting>" +
    albums.albums[index].artist +
    " • " +
    albums.albums[index].title +
    " • </span>";
  album.style.setProperty("--bg", "url(" + albums.albums[index].img + ")");
  Splitting();
  album.addEventListener("mouseover", function () {
    !playing && audio.setAttribute("src", albums.albums[index].audio);
  });
  album.addEventListener("click", function () {
    body.classList.toggle("bg-" + index);

    !playing
      ? setTimeout(() => {
          audio.play();
        }, 1000)
      : audio.pause();

    playing = !playing;
  });
});