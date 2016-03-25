/* Sections related to the whole website layout */

// Navbar menu feature when small screen size
$(function() {
    var menubar     = $('#navbar-menu');
        menu        = $('.navbar ul');
        menuHeight  = menu.height();

    $(menubar).on('click', function(e) {
        e.preventDefault();
        menu.slideToggle();
    });

    $(window).resize(function(){
        var w = $(window).width();
        if(w > 600 && menu.is(':hidden')) {
            menu.removeAttr('style');
        }
    });
});

// Scroll at front page
$(".next").click(function() {
   $('html,body').animate({ scrollTop:$(this).parent().next().offset().top}, 'slow');});

// switching between timeline & map

$(function() {
    // Define the representation methods in enum way
    var display = {"TIMELINE": 1, "MAP":2};
    Object.freeze(display);

    // Default: timeline
    var currentDisplay = display.TIMELINE;
    var firstLoadMap = true;
    var mapButton = $('#selectMap');
    var timelineButton = $('#selectTimeline');

    // Change views when clicked
    $("#selectTimeline").click(function() {
        if (currentDisplay !== display.TIMELINE) {
            // Hide the map view, then show the timeline
            $('.map-container').slideToggle(250);
            $('.timeline-container').slideToggle(250);

            // Switch the active button CSS
            timelineButton.addClass('button-active');
            mapButton.removeClass('button-active');

            currentDisplay = display.TIMELINE;
        }
    });

    $("#selectMap").click(function() {
        if (currentDisplay !== display.MAP) {
            // Hide the timeline, then show the map view
            $('.timeline-container').slideToggle(250);
            if (firstLoadMap) {
                $('.map-container').slideToggle({
                    complete:function (){
                        initMap();
                        // google.maps.event.trigger(map, 'resize');
                    },
                    duration:'slow'
                });
                firstLoadMap = false;
            }
            else {
                $('.map-container').slideToggle(250);
            }

            // Switch the active button CSS
            timelineButton.removeClass('button-active');
            mapButton.addClass('button-active');

            currentDisplay = display.MAP;
        }
    });
});



/* Timeline Section */

// Initialize timeline:::::
$(function() {
    // Move the timeline-keyword according to their height
    var words = $('.timeline-keyword');
    var heights = "";
    for (i = 0; i < words.length; i++) {
        if (i%2 === 0) {
            if ($(words[i]).height() > 50) {
                ($(words[i]).css("margin-top", "-50px"));
            }
            else if ($(words[i]).height() > 30) {
                ($(words[i]).css("margin-top", "-30px"));
            }
        }
    }

    // Show the right part of the timeline first
    var containerLength = $('.timeline-container').width();
    var displacement = $('.timeline').width() - containerLength + 80;
    $('.timeline').css('margin-left', -displacement + 'px');
});

// Allow the click of left and right timeline
$(function() {
    $distance = -50;

    function timelineMoveRight() {
        $('.timeline').stop().animate(
            {marginLeft: '+='+$distance}, 250, 'linear', timelineMoveRight
        );
    }
    function timelineMoveLeft() {
        $('.timeline').stop().animate(
            {marginLeft: '+='+-$distance}, 500, 'linear', timelineMoveLeft
        );
    }

    function stop() {
        $('.timeline').stop();
    }

    $('#timeline-left').hover(timelineMoveLeft, stop);
    $('#timeline-right').hover(timelineMoveRight, stop);
});

    // var a = $('.timeline').outerWidth() - $('.timeline').innerWidth();
    // alert(a);
    // $('.timeline').css('margin-left','-300px');
// );

// $(function() {
//     $('.timeline-keyword').bind('click', function (event) {
//         // Tune the height and width if too big
//         var width = $(window).width();
//         var popup_left = event.pageX;
//         if( (popup_left+270) >= width) {
//             popup_left -= 270;
//         }

//         var height = $(window).height();
//         var popup_top = event.pageY;
//         var popup_height = $('#timeline-news-info').height();
//         // alert(popup_height + " " + popup_top + " " + height);
//         if ( (popup_top + popup_height) >= height - 60) {
//             popup_top -= popup_height / 6;
//         }
//         $('#timeline-news-info').css('left', popup_left);
//         $('#timeline-news-info').css('top', popup_top);
//         $('#timeline-news-info').css('display', 'inline');
//         $('#timeline-news-info').css('position', 'absolute');
//         $('#popup-decoration').css('display', 'block');
//     });
// });

// $(function() {
//     $('#timeline-news-hide').bind('click', function() {
//         $('#timeline-news-info').hide();
//         $('#popup-decoration').hide();
//     })
// });

// $(document).click(function(e) {
//     if ($('#timeline-news-info').css('display') != 'none') {
//         if (e.target.id != 'timeline-news-info' && !$('#timeline-news-info').find(e.target).length) {
//             $('#timeline-news-info').hide();
//         }
//     }
//     else {
//         // alert("Hi");
//     }
// });

$(function() {
    $('.timeline-day li').bind('click', function() {

    })
});



$(document).on('ready', function(){
    $modal = $('.modal-frame');
    $overlay = $('.modal-overlay');

    /* Need this to clear out the keyframe classes so they dont clash with each other between ener/leave. Cheers. */
    $modal.bind('webkitAnimationEnd oanimationend msAnimationEnd animationend', function(e){
      if($modal.hasClass('state-leave')) {
        $modal.removeClass('state-leave');
      }
    });

    $('.close').on('click', function(){
      $overlay.removeClass('state-show');
      $modal.removeClass('state-appear').addClass('state-leave');
    });

    $('.timeline-keyword').on('click', function(){
      $overlay.addClass('state-show');
      $modal.removeClass('state-leave').addClass('state-appear');
    });

  });

/* Map Sections */

var map;
var markers = [];
var infoboxes = [];

    //!!!MarkerGenLineStart
var markList = [
    [30.6586    , 104.0647, '10', 'Chendu panda born two childs!'],
    [22.303, 114.175, 'B', 'Hong Kong University of Sience and Techonology is regarded as University of Stress and Tension'],
    [15.6586    , 160.0647, 'C', 'Chicago Bull Wins again!'],
    [21.6586    , 224.0647, 'D', 'Hong Kong is independent!'],
];
    //!!!MakerGenLineEnd


function initMap() {
    var center;

    center = new google.maps.LatLng(22.303, 114.010);
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 1,
        center: center,
        streetViewControl: false
    });

    google.maps.event.addDomListener(window, "resize", function() {
        var c = map.getCenter();
        google.maps.event.trigger(map, "resize");
        map.setCenter(c);
    });

    // Put the days choices on the map
    var dayChoiceDiv = document.createElement('div');
    var dayChoice = new DayChoice(dayChoiceDiv, map);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(dayChoiceDiv);

    for (var i = 0; i < markList.length; i++) {
        markers[i] = new google.maps.Marker({
            position: {lat: markList[i][0], lng: markList[i][1]},
            map: map,
            title: markList[i][3],
            label: markList[i][2],
            visible: true,
            animation: google.maps.Animation.DROP
        });

        // Create InfoWindow for marker
        // var contentString =
        //     '<div class="map-content">' +
        //         '<p>'+ markList[i][3] + '</p>' +
        //     '</div>';

        // infoboxes = new InfoBox({
        //      content: contentString,
        //      disableAutoPan: false,
        //      maxWidth: 150,
        //      pixelOffset: new google.maps.Size(-140, 0),
        //      zIndex: null,
        //      boxStyle: {
        //         background: "url('http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobox/examples/tipbox.gif') no-repeat",
        //         opacity: 0.75,
        //         width: "280px"
        //     },
        //     closeBoxMargin: "12px 4px 2px 2px",
        //     closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif",
        //     infoBoxClearance: new google.maps.Size(1, 1)
        // });


        // google.maps.event.addListener(markers[i], 'click', function() {
        //     infoboxes.open(map, this);
        //     // map.panTo(center);
        // });

        // infoboxes.open(map, markers[i]);

    }

}


function threeDaysFilter() {
    resetMarkers();
    for(var i=0; i<markList.length; i++){
        //console.log("This is out of " + i);
        if(markList[i][2]>3)
        {
            markers[i].setMap(null);
        }
    }
}

function weekFilter() {
    resetMarkers();
    for(var i=0; i<markList.length; i++) {
        //console.log("This is out of " + i);
        if(markList[i][2]>7) {
            markers[i].setMap(null);
        }
    }
}


function clearMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    //markers = [];
}

function resetMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(map);
    }
}

function DayChoice(dayChoice, map) {
    var possibleDays = ['3', '7', '15', '30', 'Days'];

    for (var i = 0; i < possibleDays.length; i++) {
        var numDay = possibleDays[i];
        var dayDiv = document.createElement('div');
        // dayDiv.className = 'day'+numDay;
        dayDiv.id = 'day' + numDay;
        dayDiv.title = 'Choose the number of days to be displayed';
        dayChoice.appendChild(dayDiv);

        var dayText = document.createElement('div');
        dayText.id = 'day' + numDay + 'Text';
        dayText.className = "dayChoiceText";
        dayText.innerHTML = numDay;
        dayDiv.appendChild(dayText);
    }
}

// FullPage.js

$(document).ready(function() {
    $('#fullpage').fullpage();
});

/*
function addMarker(lat_, lng_, title_) {
  var marker = new google.maps.Marker({
    position: {lat: lat_, lng: lng_},
    map: map
    title: title_
  });
}*/
