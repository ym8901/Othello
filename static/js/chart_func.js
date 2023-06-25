function create_chart(ctx) {
  const chartData = {
    black: [0],
    white: [0],
    draw: [0],
  };

  return (myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "黒",
          data: chartData.black,
          borderColor: "#000000",
          steppedLine: "before", // enable stepped line
        },
        {
          label: "白",
          data: chartData.white,
          borderColor: "#FFFFFF",
          steppedLine: "before", // enable stepped line
        },
        {
          label: "引き分け",
          data: chartData.draw,
          borderColor: "#008000",
          steppedLine: "before", // enable stepped line
        },
      ],
    },
    options: {
      yAxes: [
        {
          type: "linear",
          ticks: {
            beginAtZero: true,
            max: movenum,
          },
        },
      ],
    },
  }));
}

function update_chart(chart, count, result_log) {
  let i = 0;
  chart.data.labels.push(count);
  chart.data.datasets.forEach((dataset) => {
    dataset.data.push(result_log[i]);
    i++;
  });
  chart.update();
}
