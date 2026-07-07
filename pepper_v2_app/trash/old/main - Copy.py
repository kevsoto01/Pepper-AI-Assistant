import assistant, audio, controls, options, pepper, ui, utils

def run_assistant():
    
    global running, ptt_released, esc_released
    global engine, conversation_history, recognizer, microphone
    global detected_language_name
    global finished_question_time
    
    init_ui_state()
    ui_update(mode="connecting...", heard="", reply="")
    
    init_whisper()
    init_TTS()
    init_chatbot()
    
    speech_input = ""
    clean_response = ""
    
    while True:
        
        if speech_input is not clean_response:
            ui_update(mode="idle", heard=speech_input, reply=clean_response)
  
        
        skip_flag = False
        
        if exit_key():
            print("Exiting...")
            pepper_tablet_hide()
            break
        
        audio_file, should_exit = record_audio_with_preroll()
         
        finished_question_time = time.time()
        
        if should_exit:
            print("Exiting...")
            pepper_tablet_hide()
            break
                      
        if audio_file is not None:
            
            print("Saved:", audio_file)
            
            # Transcription
            print("Transcribing...")
            ui_update(mode="thinking", heard="", reply="")
            
            time_start = time.time()
            transcription = transcribe_audio(audio_file)
            time_end = time.time()
            time_elapsed = "\n("+str(int(1000*(time_end-time_start)))+" ms)"
            
            speech_input = transcription["text"]
            detected_language = transcription["language"]
            ui_update(mode="thinking", heard=speech_input, reply="")
            
            if detected_language not in ("en", "es"):
                error_msg = "Speech unclear, please try again"
                print(error_msg, "("+detected_language_name[detected_language]+")")
                log_conversation_message("CONSOLE", error_msg)
                ui_update(mode="speaking", heard="???", reply=error_msg)
                speak(error_msg, "en", False)
                ui_update(mode="idle", heard="", reply="")
                skip_flag = True
            
            if not skip_flag:
                print("\nHeard:", speech_input)
                print("Language:", detected_language_name[detected_language], time_elapsed)
                
                # Ask AI
                print("\nSending to Ollama...")
                
                time_start = time.time()
                ui_update(mode="thinking", heard=speech_input, reply="")
                response = chatbot(speech_input)
                time_end = time.time()
                time_elapsed = "\n("+str(int(1000*(time_end-time_start)))+" ms)"
                
                clean_response = clean_for_tts(censor_text(response))
                
                print("\nPepper:",clean_response,time_elapsed)
                ui_update(mode="speaking",heard=speech_input,reply=clean_response)
                
                # TTS
                print("\nConverting to speech...")
                speak(normalize_years_for_tts(response), detected_language, False)
                ui_update(mode="idle", heard=speech_input, reply=clean_response)
            
        time.sleep(0.01)
