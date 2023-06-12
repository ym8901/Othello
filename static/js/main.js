const BLACK = 1,
  WHITE = -1,
  EMPTY = 0;
let data = [];
// 石の動きを送信する例
let move = {
  x: 3,
  y: 4,
  value: 100,
};
let turn;
let GAMEBOARD;
let PASTBOARD;
let CANDIDATE;
let movenum;
let selectmode = [0, 0];
let board_size = 6; //盤面のサイズ
let value = 1; //石のポイント
let extra_mode = 0;
let numBlack = 0;
let numWhite = 0;
let paused = false;
let speed = 500;

const board = document.getElementById("board");
const h2 = document.querySelector("h2");
const counter = document.getElementById("counter");
const mode = document.getElementById("mode");
const exenum = document.getElementById("num");

document
  .querySelectorAll('[name="b-selector"],[name="w-selector"]')
  .forEach((value) => {
    value.addEventListener(`change`, setDisabled);
  });

document.querySelectorAll('[class="select"]').forEach((value) => {
  value.addEventListener("click", start);
});

document.addEventListener("keydown", (event) => {
  if (event.code === "KeyP") {
    if (selectmode[0] * selectmode[1] === 0) {
      return;
    }
    paused = !paused;
    if (paused) {
      h2.textContent = "一時停止";
      showAnime();
    } else {
      h2.textContent = "再開";
      showAnime();
      setTimeout(Autogetter, speed * 3);
    }
  } else if (event.code === "ArrowDown") {
    if (speed >= 210) {
      speed -= 10;
      h2.textContent = speed;
      showAnime();
    }
  } else if (event.code === "ArrowUp") {
    if (speed <= 790) {
      speed += 10;
      h2.textContent = speed;
      showAnime();
    }
  }
});

// 特定のラジオボタンが選択された時、一部のラジオボタンとテキストボックスを無効化する
function setDisabled() {
  var isAnyChecked = false;
  var radioGroups = document.querySelectorAll('[id="b0"],[id="w0"]');
  var targetElement = document.getElementById("exmode");
  const regex = /[^0-9]/g;
  const regexs = /[^a-zA-Z]+$/g;

  document
    .querySelectorAll('[name="b-selector"],[name="w-selector"]')
    .forEach(function (e) {
      if (e.checked) {
        if (e.id.replace(regexs, "") == "b") {
          selectmode[0] = parseInt(e.id.replace(regex, ""));
        } else {
          selectmode[1] = parseInt(e.id.replace(regex, ""));
        }
      }
    });

  radioGroups.forEach(function (radio) {
    if (radio.checked) {
      isAnyChecked = true;
    }
  });

  document.getElementById("s0").checked = true;

  if (isAnyChecked) {
    targetElement.classList.add("disabled");
  } else {
    targetElement.classList.remove("disabled");
  }
}

async function start(e) {
  if (document.getElementById("s1").checked) {
    if (!exenum.value) {
      alert("実行回数が入力されていません");
      return;
    } else if (exenum.value < 1) {
      alert("正しい実行回数を入力してください");
      return;
    }
  }

  mode.classList.add("hide");
  !exenum.value ? (movenum = 1) : (movenum = exenum.value);
  extra_mode = parseInt(e.target.id);

  fetch("/init", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      black: selectmode[0],
      white: selectmode[1],
      modenum: Number(e.target.id),
      exenum: movenum,
    }),
  })
    .then((response) => response.json())
    .then((json_data) => {
      // レスポンスの処理
      console.log(json_data);
      GAMEBOARD = json_data.gameboard;
      PASTBOARD = json_data.gameboard;
      CANDIDATE = json_data.candidate;
      turn = json_data.turn;
      showBoard();
      showCandidate();
      showturn();

      if ((turn === BLACK ? selectmode[0] : selectmode[1]) != 0) {
        setTimeout(Autogetter, speed);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// 初期化
function init() {
  for (let i = 0; i < board_size; i++) {
    const tr = document.createElement("tr");
    data[i] = Array(board_size).fill(0);
    for (let j = 0; j < board_size; j++) {
      const td = document.createElement("td");
      const disk = document.createElement("div");
      tr.appendChild(td);
      td.appendChild(disk);
      td.className = "cell";
      td.onclick = clicked;
    }
    board.appendChild(tr);
  }
}

function Autogetter() {
  if (paused) {
    return;
  }
  fetch("/move", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    body: null,
  })
    .then((response) => response.json())
    .then((json_data) => {
      // レスポンスの処理
      console.log(json_data);
      PASTBOARD = GAMEBOARD;
      GAMEBOARD = json_data.gameboard;
      CANDIDATE = json_data.candidate;
      turn = json_data.turn;
      showturn();
      showBoard();
      showCandidate();
      if (json_data.checkmate) {
        endingGame();
        return;
      }
      if (json_data.skipped) {
        showSkipped();
      }
      if ((turn === BLACK ? selectmode[0] : selectmode[1]) != 0) {
        setTimeout(Autogetter, speed);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// 盤面がクリックされた時
function clicked() {
  let y = this.parentNode.rowIndex;
  let x = this.cellIndex;
  if (CANDIDATE[y][x][turn === 1 ? 0 : 1] < 1) {
    return;
  }
  move = {
    x: x,
    y: y,
    value: value,
  };

  fetch("/move", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(move),
  })
    .then((response) => response.json())
    .then((json_data) => {
      // レスポンスの処理
      console.log(json_data);
      PASTBOARD = GAMEBOARD;
      GAMEBOARD = json_data.gameboard;
      CANDIDATE = json_data.candidate;
      turn = json_data.turn;
      showturn();
      showBoard();
      showCandidate();
      if (json_data.checkmate) {
        endingGame();
        return;
      }
      if (json_data.skipped) {
        showSkipped();
      } else {
        if ((turn === BLACK ? selectmode[0] : selectmode[1]) != 0) {
          setTimeout(Autogetter, speed);
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function showBoard() {
  for (let i = 0; i < board_size; i++) {
    for (let j = 0; j < board_size; j++) {
      const cell = board.rows[i].cells[j];
      const disk = cell.firstChild;
      if (PASTBOARD[i][j] != GAMEBOARD[i][j]) {
        cell.animate(
          { opacity: [0.4, 1] },
          { duration: 700, fill: "forwards" }
        );
      }
      disk.className =
        GAMEBOARD[i][j] >= BLACK
          ? "black"
          : GAMEBOARD[i][j] <= WHITE
          ? "white"
          : "";

      if (Boolean(extra_mode)) {
        disk.innerHTML = GAMEBOARD[i][j] === 0 ? null : GAMEBOARD[i][j];
      }
    }
  }
}

function showCandidate() {
  for (let i = 0; i < board_size; i++) {
    for (let j = 0; j < board_size; j++) {
      const cell = board.rows[i].cells[j];
      cell.className =
        CANDIDATE[i][j][turn === 1 ? 0 : 1] > 0 &&
        selectmode[turn === 1 ? 0 : 1] === 0
          ? "Possible"
          : "cell";
    }
  }
}

function showturn() {
  h2.textContent = turn === BLACK ? "黒のターン" : "白のターン";
  numBlack = numWhite = 0;
  for (let i = 0; i < board_size; i++) {
    for (let j = 0; j < board_size; j++) {
      numBlack += parseInt(GAMEBOARD[i][j] >= BLACK ? GAMEBOARD[i][j] : 0);
      numWhite += parseInt(
        GAMEBOARD[i][j] <= WHITE ? Math.abs(GAMEBOARD[i][j]) : 0
      );
    }
  }
  document.getElementById("numBlack").textContent = numBlack;
  document.getElementById("numWhite").textContent = numWhite;
  return;
}

function showSkipped() {
  h2.textContent = turn === WHITE ? "黒スキップ!" : "白スキップ!";
  showAnime();
  setTimeout(showturn, 2000);
  return;
}

function showAnime() {
  h2.animate({ opacity: [0, 1] }, { duration: speed, iterations: 3 });
}

function endingGame() {
  h2.textContent =
    numBlack > numWhite
      ? "黒の勝ち!"
      : numWhite > numBlack
      ? "白の勝ち"
      : "引き分け!";
  showAnime();
  const restartBtn = document.getElementById("restartBtn");
  restartBtn.classList.remove("hide");
  restartBtn.animate(
    { opacity: [1, 0.5, 1] },
    { delay: 2000, duration: 3000, iterations: "Infinity" }
  );

  restartBtn.addEventListener("click", () => {
    document.location.reload();
  });
}

window.onload = () => {
  init();
};
