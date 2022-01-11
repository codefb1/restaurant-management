(function($) {
  'use strict';
// Bar chart
  var barChart = new Chart(document.getElementById("bar-chart"), {
      type: 'bar',
      data: {
        labels: ["Hunger House", "Food Lounge", "Delizious", "Red Resturant", "Hunger Lounge"],
        datasets: [
          {
            label: "Population (millions)",
            backgroundColor: ["#ff0018", "#f7b11b","#ff6c60","#8663e1","#08bf6f"],
            data: [2478,5267,1734,3384,1433]
          }
        ]
      },
      options: {
        legend: { display: false },
        title: {
          display: true,
          text: 'Predicted Resturant Ratings (millions) in 2050'
        }
      }
  });
  })(jQuery);