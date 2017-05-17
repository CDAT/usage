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

    var all_users = 0;
    for(var j=0; j<total.length; j++)
    {
        all_users += total[j][1];
    }
//});

//$(document).ready(function() {
    var pie = new d3pie("pieChart", {
        /*"header": {
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
        },*/
        "footer": {
            "text":  "Out of a total of " + all_users + " active user sessions.",
            "color": "#000000",
            "fontSize": 17,
            "location": "bottom-center",/*
            "font": "open sans",
            "location": "bottom-left"*/
        },
        "size": {
            "canvasWidth": 1000,
            "pieOuterRadius": "100%"
        },
        "data": {
            "content": [
                {
                    "label": "January, " + total[0][1] + " active users",
                    "value": total[0][1],
                    "color": "#f25329"
                },
                {
                    "label": "February, " + total[1][1] + " active users",
                    "value": total[1][1],
                    "color": "#ffc840"
                },
                {
                    "label": "March, " + total[2][1] + " active users",
                    "value": total[2][1],
                    "color": "#0a356a"
                },
                {
                    "label": "April, " + total[3][1] + " active users",
                    "value": total[3][1],
                    "color": "#cc3e72"
                },
                {
                    "label": "May, " + total[4][1] + " active users",
                    "value": total[4][1],
                    "color": "#b29a76"
                },
                {
                    "label": "June, " + total[5][1] + " active users",
                    "value": total[5][1],
                    "color": "#b6c894"
                },
                {
                    "label": "July, " + total[6][1] + " active users",
                    "value": total[6][1],
                    "color": "#eec6e0"
                },
                {
                    "label": "August, " + total[7][1] + " active users",
                    "value": total[7][1],
                    "color": "#827773"
                },
                {
                    "label": "September, " + total[8][1] + " active users",
                    "value": total[8][1],
                    "color": "#9871a8"
                },
                {
                    "label": "October, " + total[9][1] + " active users",
                    "value": total[9][1],
                    "color": "#7eccbe"
                },
                {
                    "label": "November, " + total[10][1] + " active users",
                    "value": total[10][1],
                    "color": "#f25329"
                },
                {
                    "label": "December, " + total[11][1] + " active users",
                    "value": total[11][1],
                    "color": "#ffc840"
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
                "fontSize": 15
            },
            "percentage": {
                "color": "#ffffff",
                "decimalPlaces": 2
            },
            "value": {
                "color": "#adadad",
                "fontSize": 15
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
         

