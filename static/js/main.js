function addNewMessage() {
    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img src="/static/img/cute.png"/>');
}

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds){
            break;
        }
    }
}

$(document).on("click", ".sex", function() {
    $('.sex').hide();

    // get the data value of this element
    var dataValue = $(this).attr('data-value');
    $('.replies:last-child').append('<p>' + $(this).text() + '</p>');
    console.log("Sex of user: " + dataValue);
    window.sex = dataValue;

    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img class="animated fadeInUp" src="/static/img/cute.png" alt="" />');
    $('.sent:last-child').append('<p class="animated fadeInUp">What is your age?</p>');
    $('.messages ul').append('<li class="replies"></li>');
    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
    console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="6">60+</a>').hide());
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="5">41-60</a>').hide());
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="4">19-40</a>').hide());
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="3">14-18</a>').hide());
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="2">6-13</a>').hide());
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="1">3-5</a>').hide());
    $('.replies:last-child').append($('<a class="btn age btn-primary animated slideInRight" data-value="0">0-2</a>').hide());
    $('.replies:last-child > a').delay(750).fadeIn(1000);

    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
    console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
});

function addQuestion(data) {
    if (data["type"] == "diagnosis") {
        window.diagnoses = data["diagnoses"];
        populateDiagnoses();

    } else {
        questionTxt = data["question"];
        answerOpts = data["options"];
        window.patientID = data['ID'];

        $('.sent:last-child').hide();

        $('.messages ul').append('<li class="sent"></li>');
        $('.sent:last-child').append('<img src="/static/img/cute.png"/>');

        $('.sent:last-child').append("<p>" + questionTxt + "</p>");
        $('.messages ul').append('<li class="replies"></li>');
        $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
        console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);

        window.questionID = data['questionID'];

        Object.entries(answerOpts).forEach(function(x) {
            $('.replies:last-child').append($('<a class="btn answer-option btn-primary animated slideInRight" data-value="' + x[1] + '">' + x[0] + '</a>').hide());
        });
        $('.replies:last-child > a').delay(500).fadeIn(1000);
        $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
        console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
    }
}

$(document).on('click', '.age', function() {

    var age = $(this).attr('data-value');
    $('.replies:last-child').append('<p>' + $(this).text() + '</p>');
    $('.age').hide();

    data = {
        "age": age,
        "sex": window.sex
    }
    console.log(data);
    $.ajax({
        url:"/createPatientID",
        type:"POST",
        data:JSON.stringify(data),
        contentType:"application/json",
        dataType:"json",
        success: addQuestion
    });

    // add new message on the left
    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img class="animated fadeInUp" src="/static/img/cute.png"/>');
    $('.sent:last-child').append('<p class="saving animated fadeInUp"><span>.</span><span>.</span><span>.</span></p>');

    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
});

$(document).on("click", ".answer-option", function() {
    $('.answer-option').hide();

    // get the data value of this element
    var dataValue = $(this).attr('data-value');
    $('.replies:last-child').append('<p>' + $(this).text() + '</p>');

    data = {
        "questionID": window.questionID,
        "answer": dataValue,
        "patientID": window.patientID,
        "sex": window.sex
    }

    $.ajax({
        url:"/receiveResponse",
        type:"POST",
        data:JSON.stringify(data),
        contentType:"application/json",
        dataType:"json",
        success: addQuestion
    });

    // add new message on the left
    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img class="animated fadeInUp" src="/static/img/cute.png"/>');
    $('.sent:last-child').append('<p class="saving animated fadeInUp"><span>.</span><span>.</span><span>.</span></p>');
    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
    console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
});

function populateDiagnoses() {
    var diagnoses = window.diagnoses;
    $('.sent:last-child').hide();
    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img src="/static/img/cute.png"/>');
    $('.sent:last-child').append("<p>I've found some diagnoses that may be helpful!</p>");
    $('.diagnoses').css('display', 'block');
    diagnoses.forEach(function(element) {
        $('.diagnoses').append('<section class="disease"></section>');
        $('.disease:last-child').append('<h4>' + element[0] + '</h4>');
        $('.disease:last-child').append('<p>' + element[1] + '</p>');
        $('.disease:last-child').append('<a href="' + element[2] + '"> » Find out more</a>');
    });
    $([document.documentElement, document.body]).stop().animate({ scrollTop: $("#resultsection").offset().top}, 1000);
}

$(document).one("click", '#robotIcon, .speech-bubble', function() {
    $([document.documentElement, document.body]).stop().animate({ scrollTop: $("#chatsection").offset().top}, 1000);
    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append($('<img class="animated fadeInUp" src="/static/img/cute.png" alt="Friendly RoboDoc"/>').hide());
    $('.sent:last-child').append($('<p class="animated fadeInUp">Welcome to RoboDoc, your friendly local medical assistant! To help me diagnose your disease, please answer a few questions for me.</p>').hide());
    $('.sent:last-child').children("img, p").delay(1000).fadeIn(1);

    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append($('<img class="animated fadeInUp" src="/static/img/cute.png" alt="Friendly RoboDoc"/>').hide());
    $('.sent:last-child').append($('<p class="animated fadeInUp">What is your biological sex?</p>').hide());
    $('.sent:last-child').children("img, p").delay(2750).fadeIn(1);

    $('.messages ul').append('<li class="replies"></li>');
    $('.replies:last-child').append($('<a class="btn sex btn-primary animated slideInRight" data-value="2">Other</a>').hide());
    $('.replies:last-child').append($('<a class="btn sex btn-primary animated slideInRight" data-value="1">Female</a>').hide());
    $('.replies:last-child').append($('<a class="btn sex btn-primary animated slideInRight" data-value="0">Male</a>').hide());
    $('.replies:last-child > a').delay(3500).fadeIn(1000);
});
