$(document).ready(function() {
    var stuff = document.getElementById('coords').innerHTML; 
    var months = document.getElementById('months').innerHTML; 
    var okay = $.makeArray(months);
    var monthdata = document.getElementById('monthdata').innerHTML; 
    //monthdata = $.makeArray(monthdata);
    var copy = months;
    copy = copy.split(",");
    console.log(copy);
    console.log(okay);

    var parsedTest = JSON.parse(months);
    var sparsedTest = JSON.parse(monthdata);
    console.log(parsedTest);
    console.log(sparsedTest);
    //console.log(stuff);
    //console.log(typeof(months));
    //console.log(monthdata);

    var total = [];
    for(var i = 0; i < parsedTest.length; i++)
    {
        //total.push(months[i]);
        var nested = [];
        nested.push(parsedTest[i], sparsedTest[i]);
        total.push(nested);
        //total.push(parsedTest[i], sparsedTest[i]);
    } 
    console.log(total[0][0]);
    var max = Math.max.apply(Math,sparsedTest);
    console.log(max);

//});


//$(document).ready(function() {
    var pie = new d3pie("pieChart", {
        "header": {
            "title": {
                "text": "Percentage of session start dates by month",
                "fontSize": 24,
                "font": "open sans"
            },
            "subtitle": {
                "text": "Note: if a month is not displayed, it means there were 0 start date visits for that month.",
                "color": "#999999",
                "fontSize": 12,
                "font": "open sans"
            },
            "titleSubtitlePadding": 9
        },
        "footer": {
            "color": "#999999",
            "fontSize": 10,
            "font": "open sans",
            "location": "bottom-left"
        },
        "size": {
            "canvasWidth": 590,
            "pieOuterRadius": "90%"
        },
        "data": {
            "content": [
                {
                    "label": "January",
                    "value": total[0][1],
                    "color": "#69969C"
                },
                {
                    "label": "February",
                    "value": total[1][1],
                    "color": "#427A82"
                },
                {
                    "label": "March",
                    "value": total[2][1],
                    "color": "#246068"
                },
                {
                    "label": "April",
                    "value": total[3][1],
                    "color": "#0E464E"
                },
                {
                    "label": "May",
                    "value": total[4][1],
                    "color": "#012E34"
                },
                {
                    "label": "June",
                    "value": total[5][1],
                    "color": "#6E91A1"
                },
                {
                    "label": "July",
                    "value": total[6][1],
                    "color": "#467386"
                },
                {
                    "label": "August",
                    "value": total[7][1],
                    "color": "#27576B"
                },
                {
                    "label": "September",
                    "value": total[8][1],
                    "color": "#103D50"
                },
                {
                    "label": "October",
                    "value": total[9][1],
                    "color": "#022636"
                },
                {
                    "label": "November",
                    "value": total[10][1],
                    "color": "#69969C"
                },
                {
                    "label": "December",
                    "value": total[11][1],
                    "color": "#427A82"
                }
            ]
        },
        "labels": {
            "outer": {
                "pieDistance": 32
            },
            "inner": {
                "hideWhenLessThanPercentage": 3
            },
            "mainLabel": {
                "fontSize": 11
            },
            "percentage": {
                "color": "#ffffff",
                "decimalPlaces": 0
            },
            "value": {
                "color": "#adadad",
                "fontSize": 11
            },
            "lines": {
                "enabled": true
            },
            "truncation": {
                "enabled": true
            }
        },
        "effects": {
            "pullOutSegmentOnClick": {
                "effect": "linear",
                "speed": 400,
                "size": 8
            }
        },
        "misc": {
            "gradient": {
                "enabled": true,
                "percentage": 100
            }
        }
    });
});
         

