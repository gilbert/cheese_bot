#!/bin/bash                                                                                                  
for file in example_bots/*.jar                                                                               
do                                                                                                           
    player_1_counter=0                                                                                       
    player_2_counter=0                                                                                       
    player_2_turn_counter=0                                                                                  
    echo "Bot: $file"                                                                                        
    for i in {1..100}                                                                                        
    do                                                                                                       
        #echo "Map: $i"                                                                                      
        RES=`java -jar tools/PlayGame.jar maps/map$i.txt 500 500 log.txt "java -jar $file" "python MyBot.py" 2>&1 |
                 tail -n 3 | egrep "^Turn|^Player"`                                                          

        TURN=`echo $RES | sed 's/Turn \([0-9]*\) .*/\1/g'`                                                   
        RES2=`echo $RES | grep 'Player [0-9] Wins!'`
        if [ "$RES2" = "Player 1 Wins!" ] ; then
            player_1_counter=`expr $player_1_counter + 1`                                                    
        else                                                                       
            player_2_counter=`expr $player_2_counter + 1`                                                    
            player_2_turn_counter=`expr $player_2_turn_counter + $TURN`                                      
        fi  
        
    done                                                                                                     
    player_2_turn_counter=`expr $player_2_turn_counter / 100`                                                
    echo "$file : $player_2_counter/100, avg turns: $player_2_turn_counter"                                  
done