// ==========================================
// GLOBAL VARIABLES
// ==========================================

let predictionData = [];

let priceChart = null;
let errorChart = null;

let currentRange = 50;


// ==========================================
// LOAD CSV
// ==========================================

Papa.parse("../prediction_results.csv", {

    download: true,

    header: true,

    skipEmptyLines: true,

    complete: function(results) {

        console.log("CSV loaded successfully");

        predictionData = results.data;

        console.log("Total rows:", predictionData.length);

        initializeDashboard();

    },

    error: function(error) {

        console.error("CSV loading error:", error);

        alert(
            "Unable to load prediction_results.csv"
        );

    }

});


// ==========================================
// INITIALIZE DASHBOARD
// ==========================================

function initializeDashboard() {

    cleanData();

    updateLatestPrice();

    updatePredictionCount();

    createPriceChart();

    createErrorChart();

    displayTable(predictionData);

}


// ==========================================
// CLEAN CSV DATA
// ==========================================

function cleanData() {

    predictionData = predictionData
        .filter(row => row.timestamp)
        .map(row => {

            return {

                timestamp: row.timestamp,

                actual_price:
                    parseFloat(row.actual_price),

                predicted_price:
                    parseFloat(row.predicted_price),

                error:
                    parseFloat(row.error)

            };

        });

}


// ==========================================
// UPDATE LATEST PRICE
// ==========================================

function updateLatestPrice() {

    if (predictionData.length === 0)
        return;


    const latest =
        predictionData[predictionData.length - 1];


    document.getElementById(
        "latestPrice"
    ).textContent =
        "$" + latest.actual_price.toFixed(2);


    document.getElementById(
        "latestTime"
    ).textContent =
        formatDate(latest.timestamp);

}


// ==========================================
// UPDATE COUNT
// ==========================================

function updatePredictionCount() {

    document.getElementById(
        "predictionCount"
    ).textContent =
        predictionData.length.toLocaleString();

}


// ==========================================
// FORMAT DATE
// ==========================================

function formatDate(dateString) {

    const date = new Date(dateString);

    return date.toLocaleString();

}


// ==========================================
// GET CHART DATA
// ==========================================

function getChartData() {

    if (currentRange === "all") {

        return predictionData;

    }


    return predictionData.slice(
        0,
        currentRange
    );

}


// ==========================================
// PRICE CHART
// ==========================================

function createPriceChart() {

    const ctx =
        document
            .getElementById("priceChart")
            .getContext("2d");


    const data =
        getChartData();


    priceChart = new Chart(ctx, {

        type: "line",

        data: {

            labels:
                data.map(row =>
                    formatTime(row.timestamp)
                ),

            datasets: [

                {

                    label:
                        "Actual Price",

                    data:
                        data.map(row =>
                            row.actual_price
                        ),

                    borderWidth: 2,

                    pointRadius: 0,

                    tension: 0.25

                },


                {

                    label:
                        "Predicted Price",

                    data:
                        data.map(row =>
                            row.predicted_price
                        ),

                    borderWidth: 2,

                    pointRadius: 0,

                    borderDash: [6, 4],

                    tension: 0.25

                }

            ]

        },


        options: {

            responsive: true,

            maintainAspectRatio: false,

            interaction: {

                mode: "index",

                intersect: false

            },


            plugins: {

                legend: {

                    labels: {

                        color: "#9ba7b8",

                        font: {

                            size: 11

                        }

                    }

                }

            },


            scales: {

                x: {

                    ticks: {

                        color: "#687589",

                        maxTicksLimit: 10

                    },

                    grid: {

                        color:
                            "rgba(255,255,255,0.04)"

                    }

                },


                y: {

                    ticks: {

                        color: "#687589",

                        callback:
                            value => "$" + value

                    },

                    grid: {

                        color:
                            "rgba(255,255,255,0.04)"

                    }

                }

            }

        }

    });

}


// ==========================================
// ERROR CHART
// ==========================================

function createErrorChart() {

    const ctx =
        document
            .getElementById("errorChart")
            .getContext("2d");


    const data =
        getChartData();


    errorChart = new Chart(ctx, {

        type: "line",

        data: {

            labels:
                data.map(row =>
                    formatTime(row.timestamp)
                ),

            datasets: [

                {

                    label:
                        "Absolute Error",

                    data:
                        data.map(row =>
                            row.error
                        ),

                    borderWidth: 2,

                    pointRadius: 0,

                    tension: 0.25

                }

            ]

        },


        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    labels: {

                        color: "#9ba7b8"

                    }

                }

            },


            scales: {

                x: {

                    ticks: {

                        color: "#687589",

                        maxTicksLimit: 10

                    },

                    grid: {

                        color:
                            "rgba(255,255,255,0.04)"

                    }

                },


                y: {

                    ticks: {

                        color: "#687589",

                        callback:
                            value => "$" + value

                    },

                    grid: {

                        color:
                            "rgba(255,255,255,0.04)"

                    }

                }

            }

        }

    });

}


// ==========================================
// FORMAT TIME
// ==========================================

function formatTime(dateString) {

    const date = new Date(dateString);

    return date.toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


// ==========================================
// RANGE BUTTONS
// ==========================================

document
    .querySelectorAll(".range-btn")
    .forEach(button => {

        button.addEventListener(
            "click",
            function() {

                document
                    .querySelectorAll(".range-btn")
                    .forEach(btn =>
                        btn.classList.remove("active")
                    );


                this.classList.add("active");


                const range =
                    this.dataset.range;


                if (range === "all") {

                    currentRange = "all";

                }
                else {

                    currentRange =
                        parseInt(range);

                }


                updateCharts();

            }

        );

    });


// ==========================================
// UPDATE CHARTS
// ==========================================

function updateCharts() {

    const data =
        getChartData();


    // PRICE CHART

    priceChart.data.labels =
        data.map(row =>
            formatTime(row.timestamp)
        );


    priceChart.data.datasets[0].data =
        data.map(row =>
            row.actual_price
        );


    priceChart.data.datasets[1].data =
        data.map(row =>
            row.predicted_price
        );


    priceChart.update();


    // ERROR CHART

    errorChart.data.labels =
        data.map(row =>
            formatTime(row.timestamp)
        );


    errorChart.data.datasets[0].data =
        data.map(row =>
            row.error
        );


    errorChart.update();

}


// ==========================================
// DISPLAY TABLE
// ==========================================

function displayTable(data) {

    const table =
        document.getElementById(
            "predictionTable"
        );


    table.innerHTML = "";


    // Show latest 20 rows

    const rows =
        data.slice(-20).reverse();


    rows.forEach(row => {

        const tr =
            document.createElement("tr");


        const actual =
            row.actual_price;


        const predicted =
            row.predicted_price;


        const directionCorrect =
            isDirectionCorrect(
                row,
                data
            );


        tr.innerHTML = `

            <td>
                ${formatDate(row.timestamp)}
            </td>

            <td>
                $${actual.toFixed(2)}
            </td>

            <td>
                $${predicted.toFixed(2)}
            </td>

            <td>
                $${row.error.toFixed(2)}
            </td>

            <td>

                <span class="result
                    ${directionCorrect
                        ? "correct"
                        : "wrong"}">

                    ${directionCorrect
                        ? "Correct"
                        : "Wrong"}

                </span>

            </td>

        `;


        table.appendChild(tr);

    });

}


// ==========================================
// DIRECTION CHECK
// ==========================================

function isDirectionCorrect(
    row,
    data
) {

    const index =
        data.indexOf(row);


    if (index === 0)
        return false;


    const previous =
        data[index - 1];


    const actualDirection =
        row.actual_price >
        previous.actual_price;


    const predictedDirection =
        row.predicted_price >
        previous.actual_price;


    return (
        actualDirection ===
        predictedDirection
    );

}


// ==========================================
// SEARCH
// ==========================================

document
    .getElementById("searchInput")
    .addEventListener(
        "input",
        function() {

            const search =
                this.value.toLowerCase();


            const filtered =
                predictionData.filter(row =>
                    row.timestamp
                        .toLowerCase()
                        .includes(search)
                );


            displayTable(filtered);

        }
    );