var change_r, change_c, change_t;

function show_regions(){
    var regions = document.getElementsByClassName("toggle_regions");
    if(!change_r){
        for(var i=0; i<regions.length; i++){
            regions[i].style.display = 'none';
        }
        change_r = 1;
    }
    else if(change_r == 1){
        for(var i=0; i<regions.length; i++){
            regions[i].style.display = 'block';
        }
        change_r = 0;
    }
}

function show_countries(){
    var countries = document.getElementsByClassName("toggle_countries");
    if(!change_c){
        for(var i=0; i<countries.length; i++){
            countries[i].style.display = 'block';
        }
        change_c = 1;
    }
    else if(change_c == 1){
        for(var i=0; i<countries.length; i++){
            countries[i].style.display = 'none';
        }
        change_c = 0;
    }
}

function show_cities(){
    var cities = document.getElementsByClassName("toggle_cities");
    if(!change_t){
        for(var i=0; i<cities.length; i++){
            cities[i].style.display = 'block';
        }
        change_t = 1;
    }
    else if(change_t == 1){
        for(var i=0; i<cities.length; i++){
            cities[i].style.display = 'none';
        }
        change_t = 0;
    }
}

function get_regions(){
    var waypts = [];
    var checked = document.getElementById('waypoints_regions');
    for(var i=0; i < checked.length; i++){
        if(checked.options[i].selected){
            waypts.push(checked[i].value);
        }
    }

    for(var j=0; j < waypts.length; j++){
        var tmp = document.getElementsByClassName(waypts[j]);
        for(var k=0; k<tmp.length; k++){
            tmp[k].style.display = 'block';
        }
    } 
}


function get_countries(){
    var waypts = [];
    var checked = document.getElementById('waypoints_countries');
    for(var i=0; i < checked.length; i++){
        if(checked.options[i].selected){
            waypts.push(checked[i].value);
        }
    }

    for(var j=0; j < waypts.length; j++){
        var tmp = document.getElementsByClassName(waypts[j]);
        for(var k=0; k<tmp.length; k++){
            tmp[k].style.display = 'block';
        }
    } 
}


function get_cities(){
    var waypts = [];
    var checked = document.getElementById('waypoints_cities');
    for(var i=0; i < checked.length; i++){
        if(checked.options[i].selected){
            waypts.push(checked[i].value);
        }
    }

    for(var j=0; j < waypts.length; j++){
        var tmp = document.getElementsByClassName(waypts[j]);
        for(var k=0; k<tmp.length; k++){
            tmp[k].style.display = 'block';
        }
    } 
}

function add_vals(what){
    var tooshay = document.getElementsByClassName(what.value);
    //alert(what.selectedIndex);
    //console.log(what.value);
    for(var k=0; k < what.length; k++){
        if(what.options[k].selected){
            console.log(what[k].value);
        }
    }
    for(var g=0; g < tooshay.length; g++){
        tooshay[g].style.display = 'block';
    }
}

$(function() {  
    $('#waypoints_regions').on('hidden.bs.select', function (e) {
      alert("what a stressful meeting");
    });
});

/*$(function() {
$('#selectpicker-container').on('hide.bs.dropdown', function () {
    alert('hide.bs.dropdown');
})
});*/

/*$(function() {
    $('#waypoints_regions').multiselect({
        onDropdownHidden: function(event){
            alert('hi');
            //window.location.reload();
        },
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        selectedClass: null,
        nonSelectedText: 'All Clients',
        includeSelectAllOption: true,
        buttonWidth: '100%',
        maxHeight: 250
    });
});*/

/*$('.selectpicker').selectpicker({
  style: 'btn-info',
  size: 4
});*/





















