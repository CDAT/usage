$(document).ready(function(){
    //new Chartkick.PieChart("chart-1", [["Blueberry", 44], ["Strawberry", 23]])
    //new Chartkick.AreaChart("chart-1", {"2013-02-10 00:00:00 -0800": 11, "2013-02-11 00:00:00 -0800": 6})
    var stuff = document.getElementById("nums").innerHTML;
    //var bruh = document.getElementById("bro").innerHTML;
    //alert(bruh);
    var data = [["United States", 44], ["Germany", 23], ["Brazil", 22]];
    //alert(typeof(data));
    //new Chartkick.GeoChart("chart-1", [["United States", 44], ["Germany", 23], ["Brazil", 22]])
    //new Chartkick.GeoChart("chart-1", data);
    //getthis();
});


function getthis(bro){
    var bruhh = bro;
    alert(bruhh)
    var arrays = [], size = 1;
    while(bruhh.length > 0){
        arrays.push(bruhh.splice(0, size));
    }
    var matrix = listToMatrix(bro, 2);
    alert(matrix);
    new Chartkick.GeoChart("chart-1", arrays);
    //return arrays;
}

function getdata(){
    var bruh = document.getElementById("forreal").innerHTML;
    var okay = bruh.split(",")
    alert(okay);
    return okay;
}


$(document).ready(function(){
      google.charts.load('current', {'packages':['geochart']});
      google.charts.setOnLoadCallback(drawRegionsMap);

      var stuff = getdata();
        

      function drawRegionsMap() {

        /*var data = google.visualization.arrayToDataTable([
          ['Country', 'Popularity'],
        ]);*/

        var data = google.visualization.arrayToDataTable([
          ['Country', 'Popularity'],
          ['Germany', 200],
          ['United States', 300],
          ['Brazil', 400],
          ['Canada', 500],
          ['France', 600],
          ['RU', 700]
        ]);

        var options = {};

        var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));

        chart.draw(data, options);
      }
});


