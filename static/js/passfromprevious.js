if (window.location.search.indexOf('query') == 1) {
    var urlParams = new URLSearchParams(window.location.search)
    var q = urlParams.get('query')
    //var r = urlParams.get('relevance')
    console.log(q)
    //console.log(r)

    // The data we are going to send in our request
    let data_package = {
        query: q//,
        //relevance: r
    };

    //filling up the result
    var segment = $("#filler");
    segment.html("");
    $("#filler").hide().append('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div></div>').fadeIn(1000);

    var url = "https://schemessg-v2.herokuapp.com/schemespredict";


    // Create our request constructor with all the parameters we need
    var headers = new Headers({
        'Content-Type': 'application/json'
        //'Content-Type': 'application/xurlencoded'
    });

    var request = new Request(url, {
        method: 'POST',
        body: JSON.stringify(data_package),
        headers: headers
    });

    // Call the fetch function passing the url of the API as a parameter
    fetch(request)
        .then((resp) => resp.json()) // Transform the data into json
        .then(function (resp) {
            // code for handling the data you get from the API
            //console.log(resp);
            var segment = $("#filler");
            segment.html("");
            for (var i = 0; i < resp.data.length; i++) {
                scheme = resp.data[i].Scheme;
                agency = resp.data[i].Agency;
                image = resp.data[i].Image;
                relevance = resp.data[i].Relevance;
                description = resp.data[i].Description;
                link = resp.data[i].Link;
                codeblock = '<div class="col-lg-12"><div class="card text-center hover-translate-y-n10 hover-shadow-lg"><div class="px-3 pb-5 pt-5"><div class="py-4"><div class="icon text-warning icon-sm mx-auto"><img height="100" width="100" src="' + image + '"></div></div><h5 class="">' + scheme + '</h5><h6 class=" mt-2 mb-0">' + agency + '</h6><p class=" mt-2 mb-0">Relevance Score: ' + relevance + '</p><p class=" mt-2 mb-0">' + description + '</p><div class="mt-4"><div class="mt-4"><a href="' + link + '" target="_blank" class="link-underline-warning"> Visit Site </a></div></div></div></div>'
                $("#filler").hide().append(codeblock).fadeIn(1000);
            }
        })
        .catch(function (err) {
            // service the errors
            console.log(err);
        });

    /*$(document).ready(function () {
        // Handler for .ready() called.
        $('body').animate({
            scrollTop: $('#filler').offset().top
        }, 800);
    });

    var newURL = location.href.split("?")[0]
    window.history.pushState('object', document.title, newURL)*/

}


//if (window.location.search.indexOf('query') == 1) {$("#filler")[0].scrollIntoView()}