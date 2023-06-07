const BLACK = 1,
  WHITE = -1;
let data = [];
let jsonData;
const board = document.getElementById("board");
const h2 = document.querySelector("h2");
const counter = document.getElementById("counter");
const mode = document.getElementById("mode");

document
  .querySelectorAll('[name="b-selector"],[name="w-selector"]')
  .forEach((value) => {
    value.addEventListener(`change`, setDisabled);
  });

document.querySelectorAll(".select").forEach((value) => {
  value.addEventListener("click", start);
});

// 特定のラジオボタンが選択された時、一部のラジオボタンとテキストボックスを無効化する
function setDisabled() {
  var isAnyChecked = false;
  var radioGroups = document.querySelectorAll(
    '[id="b-h-option"],[id="w-h-option"]'
  );
  var targetElement = document.getElementById("exmode");

  radioGroups.forEach(function (radio) {
    if (radio.checked) {
      isAnyChecked = true;
    }
  });

  document.getElementById("n-option").checked = true;

  if (isAnyChecked) {
    targetElement.classList.add("disabled");
  } else {
    targetElement.classList.remove("disabled");
  }
}

function start(e) {
  if (document.getElementById("f-option").checked) {
    if (!document.getElementById("num").value) {
      alert("実行回数が入力されていません");
      return;
    } else if (num.value < 1) {
      alert("正しい実行回数を入力してください");
      return;
    }
  }
  mode.classList.add("hide");
}

let board_size = 6; //盤面のサイズ

// 初期化
function init() {
  board.innerHTML = "";
  for (let i = 0; i < board_size; i++) {
    const tr = document.createElement("tr");
    data[i] = Array(board_size).fill(0);
    for (let j = 0; j < board_size; j++) {
      const td = document.createElement("td");
      const disk = document.createElement("div");
      tr.appendChild(td);
      td.appendChild(disk);
      td.className = "cell";
    }
    board.appendChild(tr);
  }
}

window.onload = () => {
  init();
};
