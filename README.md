Thanks to https://github.com/musikalkemist/generating-melodies-with-rnn-lstm/tree/master for huge inspiration

# Expected folder structure:
-| data
---| processed_with_mapping  #holds proccessed data
------| 0 
---------| chords-context.txt
---------| chords.txt
---------| melody.txt
------| 1
---------| chords-context.txt
---------| chords.txt
---------| melody.txt
------| 2
---------| chords-context.txt
---------| chords.txt
---------| melody.txt

---| transposed_midi  #holds midi data that will be proccessed
------| 0 
---------| midi-chords.mid
---------| midi-melody.mid
------| 1
---------| midi-chords.mid
---------| midi-melody.mid
------| 2
---------| midi-chords.mid
---------| midi-melody.mid

---| tensors  #holds music data divided into sequences
------| {idx}.pt

---| tensors_video  #holds video data divided into sequences
------| {idx}.pt

-| src
... # the same as in repo

-| weights 
---| {idx}
------| chords_model_weights.pth
------| melody_model_weights.pth