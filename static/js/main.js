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
let turn = BLACK;
let GAMEBOARD;
let PASTBOARD;
let CANDIDATE;
let movenum;
let selectmode = [0, 0];
let board_size = 6; //盤面のサイズ
let extra_mode = 0;
let numBlack = 0;
let numWhite = 0;
let paused = false;
let speed = 500;
const regex = /[^0-9]/g;
const regexs = /[^a-zA-Z]+$/g;
let values = [1, 1];
let bs;
let ws;
let bar;
let chart;

const board = document.getElementById("board");
const contents = document.getElementById("contents");
const h2 = document.querySelector("h2");
const counter = document.getElementById("counter");
const valuecounter = document.getElementById("value3");
const mode = document.getElementById("mode");
const exenum = document.getElementById("num");
const progress = document.getElementById("progress");
const ctx = document.getElementById("myChart");
const restartBtn = document.getElementById("restartBtn");

document
  .querySelectorAll('[name="b-selector"],[name="w-selector"]')
  .forEach((value) => {
    value.addEventListener(`change`, setDisabled);
  });

document.querySelectorAll('[class="select"]').forEach((value) => {
  value.addEventListener("click", start);
});

const vselect = document.getElementsByClassName("valueselect");
for (let i = 0; i < vselect.length; i++) {
  vselect[i].addEventListener("click", function (e) {
    if (values[turn === BLACK ? 0 : 1] != 0) {
      const selected = document.getElementsByClassName("selected")[0];
      selected.classList.remove("selected");
    }
    values[turn === BLACK ? 0 : 1] = e.target.id;
    e.target.classList.add("selected");
  });
}

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
    if (speed >= 110) {
      speed -= 10;
      h2.textContent = speed;
      showAnime();
    }
  } else if (event.code === "ArrowUp") {
    if (speed <= 890) {
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
  extra_mode = parseInt(e.target.id);
  if (extra_mode) {
    values[0] = values[1] = 100;
  }
  mode.classList.add("hide");
  if (movenum == 1) {
    counter.classList.remove("hide");
    if (extra_mode) {
      valuecounter.classList.remove("hide");
    }
    fetch("/init", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        black: selectmode[0],
        white: selectmode[1],
        modenum: extra_mode,
      }),
    })
      .then((response) => response.json())
      .then((json_data) => {
        // レスポンスの処理
        GAMEBOARD = json_data.gameboard;
        PASTBOARD = json_data.gameboard;
        CANDIDATE = json_data.candidate;
        turn = json_data.turn;
        if (extra_mode) {
          bs = json_data.bs;
          ws = json_data.ws;
        }
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
  } else {
    bar = new ProgressBar.Circle(progress, {
      color: "#aaa",
      // This has to be the same size as the maximum width to
      // prevent clipping
      strokeWidth: 4,
      trailWidth: 1,
      easing: "easeInOut",
      duration: 1400,
      text: {
        autoStyleContainer: false,
      },
      from: { color: "#aaa", width: 1 },
      to: { color: "#333", width: 4 },
      // Set default step function for all animate calls
      step: function (state, circle) {
        circle.path.setAttribute("stroke", state.color);
        circle.path.setAttribute("stroke-width", state.width);

        var value = Math.round(circle.value() * 100);
        if (value === 0) {
          circle.setText("0%");
        } else {
          circle.setText(value + "%");
        }
      },
    });
    bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    bar.text.style.fontSize = "2rem";
    bar.set(0);

    chart = create_chart(ctx);
    contents.classList.add("hide");
    ctx.parentNode.classList.remove("hide");
    runSimulation();
    return;
  }
}

function updateProgress(per) {
  bar.animate(per);
}

async function runSimulation() {
  progress.classList.remove("hide");
  let result_log = [0, 0, 0];
  for (let i = 0; i < movenum; i++) {
    await fetch("/simulate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selectmode: selectmode,
        modenum: extra_mode,
      }),
    })
      .then((response) => response.json())
      .then((json_data) => {
        updateProgress((i + 1) / movenum);
        console.log(json_data.winner);
        if (json_data.winner == BLACK) {
          result_log[0]++;
        } else if (json_data.winner == WHITE) {
          result_log[1]++;
        } else {
          result_log[2]++;
        }
        update_chart(chart,i+1,result_log)
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
  restartBtn.style.transform = "translate(-50%, 500%)";
  endingGame();
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
      PASTBOARD = GAMEBOARD;
      GAMEBOARD = json_data.gameboard;
      CANDIDATE = json_data.candidate;
      turn = json_data.turn;
      if (extra_mode) {
        bs = json_data.bs;
        ws = json_data.ws;
      }
      showturn();
      showBoard();
      showCandidate();
      if (json_data.checkmate) {
        endingGame(json_data.checkmate);
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
  if (values[turn === BLACK ? 0 : 1] === 0) {
    alert("残っている石を選択してください");
    return;
  }
  move = {
    x: x,
    y: y,
    value: values[turn === BLACK ? 0 : 1],
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
      PASTBOARD = GAMEBOARD;
      GAMEBOARD = json_data.gameboard;
      CANDIDATE = json_data.candidate;
      turn = json_data.turn;
      if (extra_mode) {
        bs = json_data.bs;
        ws = json_data.ws;
      }
      showturn();
      showBoard();
      showCandidate();
      if (json_data.checkmate) {
        endingGame(json_data.checkmate);
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
      if (extra_mode) {
        disk.classList.add(
          Math.abs(GAMEBOARD[i][j]) === 100
            ? "red"
            : Math.abs(GAMEBOARD[i][j]) === 50
            ? "orange"
            : "blue"
        );
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
      console.log(
        CANDIDATE[i][j][turn === 1 ? 0 : 1],
        selectmode[turn === 1 ? 0 : 1]
      );
    }
  }
}

function showturn() {
  h2.textContent = turn === BLACK ? "黒のターン" : "白のターン";
  for (let i = 0; i < vselect.length; i++) {
    if (turn === WHITE) {
      vselect[i].classList.add("w");
    } else {
      vselect[i].classList.remove("w");
    }
  }

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
  if (extra_mode) {
    const spans = document.getElementsByClassName("stock");

    for (let i = 0; i < 3; i++) {
      if (vselect[i].classList.contains("selected")) {
        vselect[i].classList.remove("selected");
      }
    }
    if (values[turn === BLACK ? 0 : 1] > 0) {
      let value =
        values[turn === BLACK ? 0 : 1] == 100
          ? 0
          : values[turn === BLACK ? 0 : 1] == 50
          ? 1
          : 2;
      vselect[value].classList.add("selected");
    }
    for (let i = 0; i < 3; i++) {
      spans[i].textContent = turn === BLACK ? bs[i] : ws[i];
      vselect[i].classList.remove("disabled");
      if ((turn === BLACK ? bs[i] : ws[i]) === 0) {
        if (vselect[i].classList.contains("selected")) {
          vselect[i].classList.remove("selected");
          values[turn === BLACK ? 0 : 1] = 0;
        }
        vselect[i].classList.add("disabled");
      }
    }
  }
  return;
}

function showSkipped() {
  h2.textContent = turn === WHITE ? "黒スキップ!" : "白スキップ!";
  showAnime();
  setTimeout(showturn, speed * 3);
  return;
}

function showAnime() {
  h2.animate({ opacity: [0, 1] }, { duration: speed, iterations: 3 });
}

function endingGame(result) {
  h2.textContent =
    numBlack > numWhite
      ? "黒の勝ち!"
      : numWhite > numBlack
      ? "白の勝ち!"
      : movenum > 1
      ? "完了!"
      : "引き分け!";
  showAnime();
  restartBtn.classList.remove("hide");
  restartBtn.animate(
    { opacity: [1, 0.5, 1] },
    { delay: speed * 3, duration: speed * 6, iterations: "Infinity" }
  );

  restartBtn.addEventListener("click", () => {
    document.location.reload();
  });
}

function data_load() {
  fetch("/load", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    body: null,
  })
    .then((response) => response.json())
    .then((json_data) => {
      // レスポンスの処理
      if (json_data.winner === 0) {
        extra_mode = json_data.mode;
        selectmode = json_data.selectmode;
        GAMEBOARD = json_data.gameboard;
        PASTBOARD = json_data.gameboard;
        CANDIDATE = json_data.candidate;
        turn = json_data.turn;
        values = [1, 1];
        if (extra_mode) {
          bs = json_data.bs;
          ws = json_data.ws;
          valuecounter.classList.remove("hide");
          values = [0, 0];
        }
        mode.classList.add("hide");
        counter.classList.remove("hide");
        console.log(CANDIDATE);
        showBoard();
        showCandidate();
        showturn();
        for (let i = 0; i < 3; i++) {
          if (vselect[i].classList.contains("selected")) {
            vselect[i].classList.remove("selected");
          }
        }

        if ((turn === BLACK ? selectmode[0] : selectmode[1]) != 0) {
          paused = true;
        }
      } else {
        return;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

window.onload = () => {
  init();
  data_load();
};
