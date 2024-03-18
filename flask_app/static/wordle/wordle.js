//Initial Variables
word_len = 0; //Length of the word of the day
row_guess = ""; //The guess by the player
current_row = 0; //Current row of the wordle
allow_input = true; //allow keyboard input

// Converts a number into an id for a wordle tile
function convertToID(num){
  return(current_row.toString()+num.toString());
}

//Used to display the leaderboard 
//Hides the wordle and keyboard 
//Iterates through wordle data which holds the leaderboard gained from database
function displayLeaderboard(wordle_data){
    const leaderboard = document.getElementById('leaderboard')
    leaderboard.style.display = 'block';
    document.getElementById('wordleContent').style.display = 'none';
    document.getElementById('keyboardContainer').style.visibility = 'hidden';

    for(var i=0; i<5; i++){
      const entry_id = "entry_".concat(i.toString());
      const color_id = "score_".concat(i.toString());
      document.getElementById(entry_id).textContent = wordle_data[color_id];
    }
}


// Triggered by an enter
// Processes the word -> changes tiles colors -> Win / Lose
///https://stackoverflow.com/questions/45012378/cant-change-style-display-using-getelementbyclassname
//for changing tiles to not display
function submit(){
  allow_input = false;
  document.getElementById('wordleAlerts').textContent = "Checking Word...";
  document.getElementById('wordleAlerts').style.color = "#000000";

  const data_d = {'guess' : row_guess, 'turns' : current_row+1};
  jQuery.ajax({
      url: "/interpretGuess",
      data: data_d,
      type: "POST",
      success:function(wordle_data){        
        wordle_data = JSON.parse(wordle_data);
        
        //If it is a word
        if(wordle_data['success']){
          for(var i = 0; i < word_len; i++) { 
            // Get a string id for the wordle tile
            id = convertToID(i);
            tile = document.getElementById(id);
            tile.style.color = "#000000"; //Set color to black
            //Green 
            if(wordle_data[i] === 2){
              tile.style.backgroundColor = "#72ab82";
            }
            //Yellow 
            else if(wordle_data[i] === 1){
              tile.style.backgroundColor ="#FDFD96";
            //Gray
            }
            else{
              tile.style.backgroundColor ="#999893";
            }
          }
        document.getElementById('wordleAlerts').textContent = '\u00a0'; //Same as "", just works better w/ formatting
        //iterate row and reset guess
        current_row ++;
        row_guess = "";
        allow_input = true;


        //Win condition
        if(wordle_data['success'] === 2){
          const str = "You Win, Word Was: ".concat(wordle_data["word"]);
          document.getElementById('result').textContent = str;
          displayLeaderboard(wordle_data);
          allow_input = false;

        }
        //Lose Condition
        else if(current_row === word_len){
          const str = "You Lose, Word Was: ".concat(wordle_data["word"]);
          document.getElementById('result').textContent = str;            
          displayLeaderboard(wordle_data);
          allow_input = false;

        }
        }
        // If it is not a word
        else{
          document.getElementById('wordleAlerts').style.color = "#FF0000";
          document.getElementById('wordleAlerts').textContent = "Not a word, try again";
          allow_input = true;
        }
      }
  });
}

// Function for taking input from clicking on visual keyboard and send to interpreter below
function keyClick(letter){
  //== is used as opposed to === because integers and chars are compared
  if(letter == 8){
    key = 8;
  }
  else if(letter == 13){
    key = 13;
  }
  else{
    key=letter.charCodeAt(0);
  }
  interpretInput(letter, key);
}

//When key is pressed take input and send to interpreter below
window.onkeydown = function(event) {
  const key = event.keyCode;
  const letter = String.fromCharCode(key);
  interpretInput(letter, key);
}

//Ensures that key is a letter, backspace, or enter
//letter add to wordle tile
//backspace delete from wordle tiles
//enter call submit
function interpretInput(letter,key){
  if(allow_input){
    if(key ===13 && row_guess.length === word_len){
      submit();
    }
    else if(key >= 65 && key<=90 || key===8){
      if(key === 8){
        row_guess = row_guess.slice(0,-1);
      }
      else if(row_guess.length < word_len){
        row_guess += letter;
      }
      for(var i = 0; i < word_len; i++) { 
        id = convertToID(i);
        if(i>= row_guess.length){
          document.getElementById(id).textContent = '\u00a0';
        }
        else{
          document.getElementById(id).textContent = row_guess[i];
        }
      }
    }
  }
  
}

// Closes the instructions pop up
function closeInstructions() {
  document.getElementById('instructions').style.display = 'none';

}

//Renders the initial wordle screen (Tiles and keyboard)
//Called on initial load of wordle.html
function startGame() {
  jQuery.ajax({
      url: "/renderGame",
      type: "GET",
      success:function(tiles){
        tiles = JSON.parse(tiles);
        // https://stackoverflow.com/questions/6756104/get-size-of-json-object
        var count = Object.keys(tiles).length;
        length = Math.sqrt(count);
        word_len = length; //word of the day length

        //nested for loop to go row by row and create wordle tiles
        for(var i = 0; i < length; i++) { 
          for(var j = 0; j < length; j++) { 
            const div = document.createElement('div'); 
            x = i.toString().concat(j.toString()); //Creates an id that will be assigned to the tile
            //https://stackoverflow.com/questions/16737272/text-inside-of-a-div-changes-the-position-of-it
            //https://stackoverflow.com/questions/74377526/how-to-apply-nbsp-on-html-while-using-innertext-method-in-javascript
            div.textContent = '\u00a0';
            div.classList.add("tile"); //Add class= "tile" 
            div.id = x; //set id="00", or "01", etc

            //Calculates a good size for each tile to fit no matter what n is
            const tile_width = ((90.0/length)).toString().concat("%");
            div.style.width = tile_width;
            div.style.height = tile_width;

            // https://www.quora.com/How-do-I-repeat-same-element-in-HTML-without-including-them-over-and-over
            const body = document.getElementById('wordleContent'); 
            body.appendChild(div); 
          }
        }
        }
  });
}


