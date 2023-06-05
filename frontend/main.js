const BLACK = 1,
  WHITE = -1;
let data = [];

const board = document.getElementById("board");
const h2 = document.querySelector("h2");
const counter = document.getElementById("counter");

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
