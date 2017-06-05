function loadpiechart(thiso){
  google.charts.load('current', {'packages':['corechart']});
  google.charts.setOnLoadCallback(drawChart);

  function drawChart() {

    var okay = thiso;
    var all_it = new Array();
    var jan = 0;
    var feb = 0;
    var march = 0;
    var april = 0;
    var may = 0;
    var june = 0;
    var july = 0;
    var aug = 0;
    var sept = 0;
    var oct = 0;
    var nov = 0;
    var dec = 0;

    for(var i = 0; i < okay.length; i++) {
       if(okay[i] == 1){
            jan += 1; 
       }
       if(okay[i] == 2){
            feb += 1;
       }
       if(okay[i] == 3){
            march += 1;
       }
       if(okay[i] == 4){
            april += 1;
       }
       if(okay[i] == 5){
            may += 1;
       }
       if(okay[i] == 6){
            june += 1;
       }
       if(okay[i] == 7){
            july += 1;
       }
       if(okay[i] == 8){
            aug += 1;
       }
       if(okay[i] == 9){
            sept += 1;
       }
       if(okay[i] == 10){
            oct += 1;
       }
       if(okay[i] == 11){
            nov += 1;
       }
       if(okay[i] == 12){
            dec += 1;
       }
    }

    var data = google.visualization.arrayToDataTable([
      ['Month', 'Number of Sessions'],
      ['January',     Number(jan)],
      ['February',     Number(feb)],
      ['March',     Number(march)],
      ['April',     Number(april)],
      ['May',     Number(may)],
      ['June',     Number(june)],
      ['July',     Number(july)],
      ['August',     Number(aug)],
      ['September',     Number(sept)],
      ['October',      Number(oct)],
      ['November',  Number(nov)],
      ['December', Number(dec)]
    ]);

    var options = {
      title: 'Number of sessions for 2016'
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));
    chart.draw(data, options);
  }
}
