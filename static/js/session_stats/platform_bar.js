$(document).ready(function(){
    $('[data-toggle="popover"]').popover();   
});

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip({
           animated : 'fade',
           placement : 'bottom',
           container: 'body'
    }); 
});
