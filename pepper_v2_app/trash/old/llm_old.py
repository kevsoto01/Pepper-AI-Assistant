# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:04:06 2026

@author: kevso
"""

# def init_chatbot():
    
#     print("Loading LLM...")
   
#     try:  
#      chat(
#          model      = MODEL,
#          messages   = [{'role': 'user', 'content': 'hi'}],
#          options     = OPTIONS,
#          keep_alive  = LIFETIME
#      )
#      print("Chatbot warmed up.")
     
#     except Exception as e:
#         print("Warmup failed:", e)


# def chatbot(prompt):
       
#     response = chat(
#         model       = MODEL,
#         messages    = prompt,
#         options     = OPTIONS,
#         keep_alive  = LIFETIME
#     )
    
#     assistant_text = response['message']['content'].strip()
    
#     return assistant_text