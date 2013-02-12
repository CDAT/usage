<?php	include_once('check.php');?>
<html>
  <head>
    <title>Bar Chart</title>
    <script src="http://d3js.org/d3.v3.min.js"></script>
    <style type="text/css">
			body {
  			font: 15px sans-serif;
			}
			.bar rect {
  			fill: steelblue;
			}
			.bar text.value {
  			fill: black;
			}
			.axis {
  			shape-rendering: crispEdges;
			}
			.axis path {
  			fill: none;
			}
			.x.axis line {
  			stroke: #fff;
  			stroke-opacity: .8;
			}
			.y.axis path {
  			stroke: black;
			}
    </style>
  </head>
	<body>
		<h1>UVCDAT Users Per OS</h1>
		<?php
			date_default_timezone_set('America/Los_Angeles');
			$date = date("Y-m-d H:i:s");
			echo "<p>data sample as of: " . $date . " PST </p>";
		?>
    <script type="text/javascript">

			var margin = {top: 30, right: 50, bottom: 10, left: 50},
    			width = 600 - margin.right - margin.left,
    			height = 200 - margin.top - margin.bottom;

			var format = d3.format(",.0f");
	
			var x = d3.scale.linear()
  			.range([0, width]);

			var y = d3.scale.ordinal()
				.rangeRoundBands([0, height], .5);

			var xAxis = d3.svg.axis()
    		.scale(x)
    		.orient("top")
    		.tickSize(0);

			var yAxis = d3.svg.axis()
    		.scale(y)
    		.orient("left")
    		.tickSize(0);

			var svg = d3.select("body").append("svg")
    		.attr("width", width + margin.right + margin.left)
    		.attr("height", height + margin.top + margin.bottom)
  			.append("g")
    		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

			d3.csv("data.csv", function(data) {
  			// Parse numbers, and sort by value.
  			data.forEach(function(d) { d.value = +d.value; });
  			data.sort(function(a, b) { return b.value - a.value; });

  			// Set the scale domain.
  			x.domain([0, d3.max(data, function(d) { return d.value; })]);
  			y.domain(data.map(function(d) { return d.name; }));

  			var bar = svg.selectAll("g.bar")
      		.data(data)
    			.enter().append("g")
      		.attr("class", "bar")
      		.attr("transform", function(d) { return "translate(0," + y(d.name) + ")"; });

  			bar.append("rect")
      		.attr("width", function(d) { return x(d.value); })
      		.attr("height", y.rangeBand());

  			bar.append("text")
      		.attr("class", "value")
      		.attr("x", function(d) { return x(d.value); })
      		.attr("y", y.rangeBand() / 2)
      		.attr("dx", -0)
      		.attr("dy", ".35em")
      		.attr("text-anchor", "top")
      		.text(function(d) { return format(d.value); });

  			svg.append("g")
      		.attr("class", "x axis")
      		.call(xAxis);

  			svg.append("g")
      		.attr("class", "y axis")
      		.call(yAxis);
			});
    </script>
  </body>
</html>

