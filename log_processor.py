import os
import json

class log_processor:
    def __inti__(self):
        pass 

    def get_vgl_from_vglstr(self, vglstr, dataset):
        vgl = {}
        #Removing the data field as it is not necessary for encoding

        # vgl["$schema"] = "https://vega.github.io/schema/vega-lite/v3.json"
        # vgl["data"] = {"url": "data/movies.json"}
        #vgl["data"] = {"url": "/data/" + dataset + "/" + dataset +".json"}
        mark = vglstr.split(';')[0]
        encoding = vglstr.split(';')[1]
        vgl["mark"] = mark.split(':')[1]
        encodings = {}
        fields = []
        encoding = encoding.split(':')[1]
        encoding_arr = encoding.split(',')
        for encode in encoding_arr:
            one_encoding = {}
            if '<' in encode:
                regular = encode.split('<')[0]
                transform = encode.split('<')[1]

                regular_split = regular.split('-')
                if len(regular_split) != 3:
                    print ("something wrong with regular string.")
                field = regular_split[0]
                attr_type = regular_split[1]
                encoding_type = regular_split[2]

                one_encoding["type"] = attr_type
                if field != '':
                    one_encoding["field"] = field
                    fields.append(field)

                transform_split = transform.split('>')
                transform_type = transform_split[0]
                transform_val = transform_split[1]

                if transform_type == "bin":
                    one_encoding["bin"] = True
                else:
                    one_encoding[transform_type] = transform_val

                #encodings[encoding_type] = one_encoding

            else:
                encode_split = encode.split('-')
                if len(encode_split) != 3:
                    print ("something wrong with encode string.")

                field = encode_split[0]
                attr_type = encode_split[1]
                encoding_type = encode_split[2]

                one_encoding["type"] = attr_type
                if field != '':
                    one_encoding["field"] = field
                    fields.append(field)
                else:
                    print ("something wrong:")
                    print (vglstr)

                ## for bs Flight_Date
                if encode == "Flight_Date-nominal-row":
                    if "-x" not in vglstr:
                        encoding_type = "x"
                    elif "-y" not in vglstr:
                        encoding_type = "y"
                    elif "-color" not in vglstr:
                        encoding_type = "color"
                    else:
                        encoding_type = "size"

                if "Flight_Date-nominal" in encode:
                    one_encoding["timeUnit"] = "month"

                ## for movie Release_Date
                if encode == "Release_Date-nominal-row":
                    if "-x" not in vglstr:
                        encoding_type = "x"
                    elif "-y" not in vglstr:
                        encoding_type = "y"
                    elif "-color" not in vglstr:
                        encoding_type = "color"
                    else:
                        encoding_type = "size"

                if "Release_Date-nominal" in encode:
                    one_encoding["timeUnit"] = "month"

            #Sanad: We do not need the height width etc. field right now
            # if "field" in one_encoding:
            #     if one_encoding["field"] == "Title":
            #         if encoding_type == "x":
            #             vgl["width"] = 3200
            #         else:
            #             vgl["height"] = 18000
            #     if one_encoding["field"] == "Director" or one_encoding["field"] == "Distributor":
            #         if encoding_type == "x":
            #             vgl["width"] = 3200

            encodings[encoding_type] = one_encoding

        vgl["encoding"] = encodings
        vgl_json = json.dumps(vgl, ensure_ascii=False)
        return vgl_json

    # function for removing repeated entries
    def del_repeat_entries(self, data):
        # Initialize a list to store filtered entries
        filtered_data = []
        # Iterate through the data and filter entries
        prev_value = None
        prev_entry = None
        for entry in data:
            
            try:
                if('mark' not in entry['Value']):
                    continue
            except KeyError:
                # print(entry) #There is not field called "Value"
                continue

            current_value = entry['Value']
            if entry["Interaction"] == 'typed in answer':
                prev_entry = entry
                continue
            # Check if the current entry has a different value from the previous entry
            if current_value != prev_value:
                filtered_data.append(entry)

            prev_value = current_value
            prev_entry = entry
        return filtered_data
    
    #just converting the shortened format to original vegalite (as it is)
    def get_vega_lite_format2(self, vglstr):
        #Getting the vegalite json from vegalite summarized string
        vega_lite_json = self.get_vgl_from_vglstr(vglstr, "movies")
        vega_lite_spec = json.loads(vega_lite_json)

        # Convert the modified dictionary back to a JSON string

        modified_json = json.dumps(vega_lite_spec)
        json_obj = json.loads(modified_json.replace('\n', '').replace(' ', ''))

        return json_obj
    
    def get_interactions(self, filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            #Removing repeated entries
            filtered_data = self.del_repeat_entries(data)
            #Taking only the vegalite encoding specifications
            filtered_data2 = [item for item in filtered_data if 'mark:' in item['Value']]
            #Converting the filtered encondings into vegalite Specifications
            filtered_data3 = [self.get_vega_lite_format2(item['Value']) for item in filtered_data2]
            return filtered_data3

        #   output_file_name = "env_" + filename
        #   # Open the output JSON file for writing
        #   with open(output_file_name, 'w') as json_file:
        #       # Write the filtered_data list to the JSON file
        #       json.dump(filtered_data3, json_file)