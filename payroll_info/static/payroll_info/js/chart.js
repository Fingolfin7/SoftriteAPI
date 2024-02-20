$(document).ready(function() {
    let baseUrl = $('#baseUrl').val();
    let canvasContainer = $('#canvas_container');

    // by default the graph shows the last week's data, so start date is 7 days ago and end date is today
    let start_date = new Date();
    start_date.setDate(start_date.getDate() - 7);

    let end_date = new Date();
    end_date.setDate(end_date.getDate());

    drawChart(formatDate(start_date), formatDate(end_date), baseUrl);

    $('#month').click(function() {
        // if the month button is clicked, the start date is 30 days ago and the end date is today
        start_date = new Date();
        start_date.setDate(start_date.getDate() - 30);

        end_date = new Date();
        end_date.setDate(end_date.getDate());
        canvasContainer.empty();
        canvasContainer.append("<canvas id='graph' width='400' height='200'></canvas>");
        drawChart(formatDate(start_date), formatDate(end_date), baseUrl);
    });

    $('#quarter').click(function() {
        // if the quarter button is clicked, the start date is 90 days ago and the end date is today
        start_date = new Date();
        start_date.setDate(start_date.getDate() - 90);

        end_date = new Date();
        end_date.setDate(end_date.getDate());

        canvasContainer.empty();
        canvasContainer.append("<canvas id='graph' width='400' height='200'></canvas>");
        drawChart(formatDate(start_date), formatDate(end_date), baseUrl);
    });

    $('#year').click(function() {
        // if the year button is clicked, the start date is 365 days ago and the end date is today
        start_date = new Date();
        start_date.setDate(start_date.getDate() - 365);

        end_date = new Date();
        end_date.setDate(end_date.getDate());

        canvasContainer.empty();
        canvasContainer.append("<canvas id='graph' width='400' height='200'></canvas>");
        drawChart(formatDate(start_date), formatDate(end_date), baseUrl);
    });

    $('#custom').click(function() {
        // if the custom button is clicked, the custom range input is shown
        $('#custom_range').show();
        $('#predefined').hide();
    });

    $('#show').click(function() {
        // if the show button is clicked, the start date and end date are set to the values in the custom range input
        start_date = new Date($('#start_date').val());
        end_date = new Date($('#end_date').val());

        if((start_date && end_date) && (start_date < end_date)) {
            canvasContainer.empty();
            canvasContainer.append("<canvas id='graph' width='400' height='200'></canvas>");
            drawChart(formatDate(start_date), formatDate(end_date), baseUrl);

            $('#custom_range').hide();
            $('#predefined').show();
        }
        else {
            alert('Invalid Date Range');
        }
    });
});

function formatDate(date) {
    let d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [month, day, year].join('-');
}

function drawChart(start_, end_, baseUrl) {
    const ctx = $('#graph');
    const avg_rate_for_period = $('#average_rate_value');

    let ajax_data = [];
    let ajax_labels = [];

    // Use the function to format your dates
    let url = baseUrl.replace('start_date', start_).replace('end_date', end_);

    $.ajax({
        url: url,
        dataType: 'json',
        success: function(data) {
            for (let i = 0; i < data.length; i++) {
                ajax_data.push(data[i].rate);
                ajax_labels.push(data[i].date);
            }

            // calculate the average rate for the period
            let sum = 0;
            for (let i = 0; i < ajax_data.length; i++) {
                sum += ajax_data[i];
            }
            let average = sum / ajax_data.length;
            avg_rate_for_period.text(average.toFixed(2));

            let myChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ajax_labels,
                    datasets: [{
                        label: 'Interbank Rate',
                        data: ajax_data,
                        fill: false,
                        backgroundColor: [
                            'rgba(99,115,255, 0.2)',
                        ],
                        borderColor: [
                            'rgb(99,115,255)',
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                parser: 'MM-DD-YYYY',
                                tooltipFormat: 'll',
                                unit: 'day',
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Rate'
                            }
                        }
                    }
                }
            });
        }
    });
}

