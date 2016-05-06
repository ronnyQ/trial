function RunningSession() {
    var myQuestionId = 0;
    var mySessionId = 0;
    var myRunTime = 0;

    this.startQuestion = function(questionId, sessionId, runTime) {
        // Send a request to the server to start the question.  The server will then respond
        // with a number of seconds until the question starts, the UI will then display a
        // countdown until the question starts and then change to a countdown until the
        // question ends.

        myQuestionId = questionId;
        mySessionId = sessionId;
        myRunTime = runTime;

        $.post('/tutor/sessions/api/start_question/', {
            'questionId': questionId,
            'sessionId': sessionId,
            'runTime': runTime
        }, function(response) {
            uiToRunning();

            // Start the countdown until the question starts
            $('#seconds-until-start').text(response.time_offset);
            $('#question-start-countdown').show();
            var countdownInterval = setInterval(function() {
                var val = $('#seconds-until-start').text();
                val--;
                $('#seconds-until-start').text(val);

                if (val == 0) {
                    clearInterval(countdownInterval);
                    $('#question-start-countdown').fadeOut(function() {
                        $('#question-progress-bars').fadeIn();
                    });
                    // This is where we call to start the countdown and polling for resposnses
                    questionRunning();
                }
            }, 1000);
        });
    };

    // This is where we start the progress bar and then start polling for responses
    questionRunning = function() {
        // Work out how often the progress bar width needs to be increased by 1% by
        var progressBarDelay = (myRunTime * 1000) / 100;
        var progressBarWidth = 0;
        var progressBarInterval = setInterval(function() {
            progressBarWidth++;
            $('#time-remaining-progress .progress-bar').width(progressBarWidth + '%');

            // Stop the progress bar once full
            if (progressBarWidth == 100) {
                clearInterval(progressBarInterval);
            }
        }, progressBarDelay);

        // Count down in seconds on the display
        var secondsRemaining = myRunTime;
        $('#seconds-remaining').text(secondsRemaining);
        var countdownInterval = setInterval(function() {
            secondsRemaining--;
            $('#seconds-remaining').text(secondsRemaining);

            if (secondsRemaining == 0) {
                clearInterval(countdownInterval);
                questionComplete();
            }
        }, 1000);
    };

    // This transitions from a running quesiton to calling the function to show the results
    questionComplete = function() {
        $('#question-countdown-container').fadeOut(function () {
            $('#gathering-responses').fadeIn();
        });

        // Wait 3 seconds to allow any remaining results to come in and then transition the UI
        setTimeout(function() {
            uiToResults();
        }, 3000);
    };

    // This sets the UI for when a question is running
    uiToRunning = function() {
        // We now replace the "run a question" div with the "question running" div
        $('#run-question').fadeOut(function() {
            $('#question-running').fadeIn();
        });
    };

    // This switches the UI to show the results for the previously run question
    uiToResults = function() {
        $('#question-running').fadeOut(function() {

        });
    };

    $(document).ready(function() {
        $('#start-question').click(function() {
            var questionId = $('#question').val();
            var sessionId = $('#session-id').val();
            var runTime = $('#question-time').val();

            runningSession.startQuestion(questionId, sessionId, runTime);

            return false;
        });
    });
}


var runningSession = new RunningSession();

$(document).ready(function() {
    // Submit the course selection form when the course in the drop down is changed
    $('#course-selection').change(function() {
        $('#course-selection-form').trigger('submit');
    });

    // Do not submit form if the item selected is not a course (i.e. the "Select a Course" option)
    $('#course-selection-form').submit(function() {
        if (isNaN(parseInt($('#course-selection').val()))) {
            return false;
        }
    });


    // Add a question option to the table
    $('#add-question-option').click(function() {
        html = $('#option-row-template').html();

        // We now need to get the number of current options to set the names on the
        // new inputs and then incrememnt the value accordingly
        option_id = $('#max-options').val();
        $('#max-options').val(parseInt(option_id)+1);

        // Replace the placeholder in the template
        html = html.replace(/#option_id#/g, option_id);

        // Append row before the second last row
        $('#option-table tr:last').before(html);

        return false; // Block default form sumbit
    });
});

$(document).on('click', '.remove-option', function() {
    $(this).closest('tr').remove();
    return false;
});
