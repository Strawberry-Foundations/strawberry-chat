# elif message.startswith("/kick "):
            #     ipa = message.replace("/kick ", "")
            #     search_string = ipa
                
            #     client.send(f"{ipa}".encode("utf8"))
                
            #     client_info = f"{addresses}"
                
            #     client_info = client_info.replace("laddr=('192.168.0.157', 8080),", "")
                
            #     for i in range(100):
            #         client_info = client_info.replace(f"<socket.socket fd={i}, family=2, type=1, proto=0,  ", "")
                    
            #     index = client_info.find(ipa)
            #     print(client)
            

                
            #     if index != -1:
            #         # Extrahiere die nächsten 5 Zeichen ab dem gefundenen Index
            #         next_five_characters = client_info[index:index + 25]
            #         print("Gefundener String:", search_string)
            #         next_five_characters = next_five_characters.replace("'", "").replace(")", "").replace(">", "").replace(":", "").replace(" ", "")
            #         print("Client Addresse:", next_five_characters)
                    
            #         index_of_comma = next_five_characters.find(",")
                    
            #         # Extrahiere den Teil des Strings, der nach dem Komma kommt
            #         text_after_comma = next_five_characters[index_of_comma + 1:]
            #         del addresses[f"('{search_string}', {text_after_comma})"]
            #         print("Text nach dem Komma:", text_after_comma)
                    
            #     else:
            #         print("String nicht gefunden.")
                    
                
                
            #     if search_string in client_info:
            #         print(f"Die Suche nach '{search_string}' war erfolgreich.")
            #     else:
            #         print(f"Die Suche nach '{search_string}' war nicht erfolgreich.")
                    
                
            #     # del users[client]