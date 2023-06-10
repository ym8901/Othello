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
let GAMEBOARD;
let movenum;
let selectmode = [0, 0];
let board_size = 6; //盤面のサイズ
let value = 1; //石のポイント

let jsonData;
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

function start(e) {
  if (document.getElementById("s1").checked) {
    if (!exenum.value) {
      alert("実行回数が入力されていません");
      return;
    } else if (exenum.value < 1) {
      alert("正しい実行回数を入力してください");
      return;
    }
  }

  !exenum.value ? (movenum = 1) : (movenum = exenum.value);

  mode.classList.add("hide");
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
      showBoard();
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

// 盤面がクリックされた時
function clicked() {
  let y = this.parentNode.rowIndex;
  let x = this.cellIndex;
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
    .then((data) => {
      // レスポンスの処理
      console.log(data);
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
      disk.className = GAMEBOARD[i][j] === BLACK ? "black" : GAMEBOARD[i][j] === WHITE ? "white" : null;
    }
  }
}

window.onload = () => {
  init();
};
