function addNewMessage() {
      $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img src="/static/img/cute.png"/>');
}

$(document).on("click", ".sex", function() {
    $('.sex').hide();

    // get the data value of this element
    var dataValue = $(this).attr('data-value');
    $('.replies:last-child').append('<p>' + $(this).text() + '</p>');
    console.log("Sex of user: " + dataValue);
    window.sex = dataValue;

    $('.messages ul').append('<li class="sent"></li>');
    $('.sent:last-child').append('<img src="/static/img/cute.png" alt="" />');
    $('.sent:last-child').append('<p>What is your age?</p>');
    $('.messages ul').append('<li class="replies"></li>');
    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
    console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="6">60+</a>');
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="5">41-60</a>');
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="4">19-40</a>');
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="3">14-18</a>');
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="2">6-13</a>');
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="1">3-5</a>');
    $('.replies:last-child').append('<a class="btn age btn-primary"  href="#" data-value="0">0-2</a>');
    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
    console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
});

function addQuestion(data) {
    if (data["type"] == "diagnosis") {
        window.diagnoses = data["diagnoses"];
        var diagnoses = window.diagnoses;
        alert(diagnoses);

        diagnoses.forEach(function(element) {
            addNewMessage();
            $('.sent:last-child').append('<p><b>' + element[0] + '</b>'+ '</p><p>' + element[1] + '</p>');
        });
            $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);

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
        $('.replies:last-child').append('<a class="btn answer-option btn-primary"  href="#" data-value="' + x[1] + '">' + x[0] + '</a>');
    });
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

    $('.sent:last-child').append('<p class="saving"><span>.</span><span>.</span><span>.</span></p>');
  
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
        "patientID": window.patientID
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
    $('.sent:last-child').append('<img src="/static/img/cute.png"/>');
    $('.sent:last-child').append('<p class="saving"><span>.</span><span>.</span><span>.</span></p>');
    $("#msgframe").stop().animate({ scrollTop: $("#msgframe").get(0).scrollHeight}, 1000);
    console.log("content scrollheight: " + $("#msgframe").get(0).scrollHeight);
});