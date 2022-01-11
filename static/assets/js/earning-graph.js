 (function($) {
  'use strict';


 /* Audience Metrics Graph */
  var audienceMetricsCtx = document.getElementById('audience-metrics-chart').getContext("2d");
  var gradientStrokePrimary = audienceMetricsCtx.createLinearGradient(0, 0, 0, 450);
  gradientStrokePrimary.addColorStop(0, '#ff0018');

  var gradientFillPrimary = audienceMetricsCtx.createLinearGradient(0, 0, 0, 450);
  gradientFillPrimary.addColorStop(0, "rgba(53,127,250,0.4)");
  gradientFillPrimary.addColorStop(1, "rgba(255,255,255,0)");

  // datasets 2
  var gradientStrokePrimaryDanger = audienceMetricsCtx.createLinearGradient(0, 0, 0, 450);
  gradientStrokePrimaryDanger.addColorStop(0, '#ec4e3f');

  var gradientFillPrimaryDanger = audienceMetricsCtx.createLinearGradient(0, 0, 0, 450);
  gradientFillPrimaryDanger.addColorStop(0, "rgba(236, 78, 63,0.4)");
  gradientFillPrimaryDanger.addColorStop(1, "rgba(255, 255, 255,0)");

  // all data
  var data_1 = [3800, 3900, 3300, 3800, 4000, 4200, 4400, 3800, 4600, 3900, 3800];
  var data_2 = [2100, 3000, 2200, 2400, 2800, 2600, 2800, 2600, 2300, 2900, 2800];
  var labels = ["12 AM", "2 PM", "4 PM", "6 PM", "8 PM", "10 PM", "12 PM", "2 PM", "6 PM", "8 AM", "10 PM"];

  var audienceMetrics = new Chart(audienceMetricsCtx, {
      type: 'line',
      data: {
          labels: labels,
          datasets: [{
              label: "Traffic",
              borderColor: gradientStrokePrimary,
              pointBorderWidth: 9,
              pointRadius: 9,
              pointBorderColor: 'transparent',
              pointHoverRadius: 8,
              pointHoverBorderWidth: 3,
              pointHoverBackgroundColor: 'white',
              pointHoverBorderColor: '#ff0018',
              pointBackgroundColor: 'transparent',
              fill: true,
              backgroundColor: gradientFillPrimary,
              borderWidth: 2,
              data: data_1
          },
          {
              label: "Sales",
              borderColor: gradientStrokePrimaryDanger,
              pointBorderWidth: 9,
              pointRadius: 9,
              pointBorderColor: 'transparent',
              pointHoverRadius: 8,
              pointHoverBorderWidth: 3,
              pointHoverBackgroundColor: 'white',
              pointHoverBorderColor: '#ec4e3f',
              pointBackgroundColor: 'transparent',
              fill: true,
              backgroundColor: gradientFillPrimaryDanger,
              borderWidth: 2,
              data: data_2
          }
          ]
      },
      options: {
          elements: {
            line: {
                tension: 0
            }
          },
          tooltips: {
            titleFontColor: '#3a3952',
            bodyFontFamily:  'Roboto',
            backgroundColor: '#FFF',
            bodyFontColor: '#878793',
            bodyFontSize: 14,
            displayColors: false,
            bodySpacing: 10,
            intersect: false,
            bodyFontStyle: 'bold',
            xPadding: 15,
            yPadding: 15,
            mode: 'index'
          },
          legend: {
            display: false,
            position: "top"
          },
          scales: {
              yAxes: [{
                  ticks: {
                      fontColor: "rgba(0,0,0,0.5)",
                      fontStyle: "bold",
                      beginAtZero: true,
                      maxTicksLimit: 200,
                      padding: 20
                  },
                  gridLines: {
                      drawTicks: false,
                      display: false
                  }

              }],
              xAxes: [{
                  gridLines: {
                      zeroLineColor: "transparent"
                  },
                  ticks: {
                      padding: 20,
                      beginAtZero: true,
                      fontColor: "rgba(0,0,0,0.5)",
                      fontStyle: "bold"
                  }
              }]
          }
      }
  });

  })(jQuery);