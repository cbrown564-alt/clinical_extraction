"""
Author: Yujian Gan
Description: 
    This script is for calling different LLMs.
"""

import openai
from openai import OpenAI, AzureOpenAI
import os, re, json, copy
from pathlib import Path
from utils.log import llm_log
import time
from datetime import datetime
from threading import Lock, RLock

import pickle
from collections import OrderedDict

import uuid
from urllib.parse import urlparse
from utils.env import load_dotenv


load_dotenv()

_CACHE_LOCKS = {}
_CACHE_LOCKS_LOCK = Lock()


def _cache_lock(cache_path):
    normalized = os.path.abspath(str(cache_path))
    with _CACHE_LOCKS_LOCK:
        if normalized not in _CACHE_LOCKS:
            _CACHE_LOCKS[normalized] = RLock()
        return _CACHE_LOCKS[normalized]


class LLM:
    def __init__(self, cache = None, cache_reasoning = True) -> None:
        self.cache_path = cache
        self.cache = None
        self.cache_capacity = 100000
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.cache_reasoning = cache_reasoning

        if self.cache_path:
            self.session_id = str(uuid.uuid4())
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()


    def _read_cache_unlocked(self):
        if not self.cache_path or not os.path.exists(self.cache_path):
            return OrderedDict()
        with open(self.cache_path, 'rb') as file:
            cache = pickle.load(file)
        if isinstance(cache, OrderedDict):
            return cache
        return OrderedDict(cache)

    def _write_cache_unlocked(self):
        if not self.cache_path:
            return
        cache_path = Path(self.cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = cache_path.with_name(f"{cache_path.name}.{self.session_id}.tmp")
        with open(tmp_path, 'wb') as file:
            pickle.dump(self.cache, file)
        os.replace(tmp_path, cache_path)

    def _cache_key(self, message):
        message_str = str(message)
        if type(message) == list and len(message) == 1 and message[0]['role'] == 'user':
            return message[0]['content']
        return message_str


    def extract_json_string(self, input_string):
        def process_colons_string(input_string, colon_positions):
            def find_string_bounds(s, start_pos, next_pos=None):
                colon_pos = s.find(':', start_pos)
                quote_start = colon_pos + 1
                
                while quote_start < len(s) and s[quote_start] in ' \t\n':
                    quote_start += 1
                
                if s[quote_start] != '"':
                    return s
                
                string_start = quote_start
                
                if next_pos:
                    substring = s[string_start:next_pos]
                    quote_end = next_pos
                    escaped = 0
                    while quote_end > string_start:
                        quote_end -= 1
                        if s[quote_end] == '"' and escaped != 2:
                            escaped += 1
                        elif s[quote_end] == '"' and escaped == 2:
                            break
                else:
                    substring = s[string_start:]
                    quote_end = len(s)
                    while quote_end > string_start:
                        quote_end -= 1
                        if s[quote_end] == '"':
                            break
                        
                actual_string = s[string_start+1:quote_end]
               
                escaped_string = ""
                is_previous_backslash = False
            
                for char in actual_string:
                    if char == '"' and not is_previous_backslash:
                        escaped_string += '\\"'
                    else:
                        escaped_string += char
                    is_previous_backslash = (char == '\\')

                new_string = s[:string_start+1] + escaped_string + s[quote_end:]
                
                return new_string
            
            result_string = input_string
            length_change = 0
            for i, pos in enumerate(colon_positions):
                end_pos = colon_positions[i+1] if i+1 != len(colon_positions) else None
                if end_pos:
                    result_string = find_string_bounds(result_string, pos + length_change, end_pos+ length_change)
                else:
                    result_string = find_string_bounds(result_string, pos + length_change)
                length_change = len(result_string) - len(input_string)
            return result_string

        def find_colons(input_string):
            pattern = r'"\s*:\s*'
            matches = []
            for match in re.finditer(pattern, input_string):
                colon_pos = match.start() + match.group().find(':')
                matches.append(colon_pos)
            return matches
        
        def clean_json_comma(json_str):
            cleaned_str = re.sub(r',\s*(\}|\])', r'\1', json_str)
            return cleaned_str

        def clean_json_string(json_str):
            def fix_json_string(json_str):
                def replace_newlines(match):
                    content = match.group(1)
                    content_fixed = content.replace("\n", "\\n")
                    return f'"{content_fixed}"'
                
                fixed_str = re.sub(r'"(.*?)"', replace_newlines, json_str, flags=re.DOTALL)
                return fixed_str
            json_str = fix_json_string(json_str)
            json_str = clean_json_comma(json_str)
            json_str = re.sub(r"'(?!s\b)", '"', json_str)
            json_str = re.sub(r'\bTrue\b', 'true', json_str)
            json_str = re.sub(r'\bFalse\b', 'false', json_str)  
            json_str = json_str.replace("\n", " ")
            json_str = re.sub(r'\(\s*("(?:[^"\\]|\\.)*?"|\w+)\s*,\s*(\d+|null|None)\s*\)', r'[\1, \2]', json_str)
            json_str = re.sub(r'\bNone\b', 'null', json_str, flags=re.IGNORECASE)
            colon_positions = find_colons(json_str)
            json_str = process_colons_string(json_str, colon_positions)
            return json_str

        start = -1
        brace_count = 0

        if not input_string:
            return ''

        try:
            json.loads(input_string)
            return input_string
        except json.JSONDecodeError as e:
            pass
        
        for i, char in enumerate(input_string):
            if char == '{':
                if brace_count == 0:
                    start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start != -1:
                    json_str = input_string[start:i+1]
                    json_str = clean_json_string(json_str)
                    
                    try:
                        json.loads(json_str)
                        return json_str
                    except json.JSONDecodeError as e:
                        print(json_str)
                        pass
                    start = -1
        return ''

    def from_cache(self, message, json_format=False, skip_cache=False):
        if self.cache_path:
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()
                return self._from_cache_unlocked(message, json_format=json_format, skip_cache=skip_cache)
        return self._from_cache_unlocked(message, json_format=json_format, skip_cache=skip_cache)

    def _from_cache_unlocked(self, message, json_format=False, skip_cache=False):
        if self.cache:
            message_str = str(message)
            if message_str not in self.cache and type(message) == list and len(message) == 1 and message[0]['role'] == 'user':
                message_str = message[0]['content']
            if message_str in self.cache:
                refresh = self.cache[message_str]
                if type(refresh) == list and len(refresh) in [3, 4]:
                    response = refresh[0]
                    input_tokens = refresh[1]
                    output_tokens = refresh[2]
                    reasoning_content = refresh[3] if len(refresh) == 4 else None
                else:
                    response = refresh
                    input_tokens = None
                    output_tokens = None
                self.cache.pop(message_str)
                if skip_cache or response is None:
                    return None, None, None
                self.cache[message_str] = refresh
                if json_format:
                    return self.extract_json_string(response), input_tokens, output_tokens
                else:
                    return response, input_tokens, output_tokens
        return None, None, None
    
    def save_to_cache(self, message, response):
        if type(response) == list and len(response) == 3:
            input_tokens = response[1]
            output_tokens = response[2]
            response = response[0]
            reasoning_content = None
        elif type(response) == list and len(response) == 4:
            input_tokens = response[1]
            output_tokens = response[2]
            reasoning_content = response[3]
            response = response[0]
        else:
            input_tokens = None
            output_tokens = None
            reasoning_content = None
        if self.cache_path and response:
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()
                cache_key = self._cache_key(message)
                if self.cache_reasoning:
                    self.cache[cache_key] = [response, input_tokens, output_tokens, reasoning_content]
                else:
                    self.cache[cache_key] = [response, input_tokens, output_tokens]
                while len(self.cache) > self.cache_capacity:
                    self.cache.popitem(last=False)
                self._write_cache_unlocked()
    
    def cache_exchange(self, message_old, message_new):
        if self.cache_path:
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()
                message_str = str(message_old)
                message_str_new = str(message_new)
                if message_str in self.cache:
                    refresh = self.cache[message_str]
                    self.cache.pop(message_str)
                    self.cache[message_str_new] = refresh
                    self._write_cache_unlocked()
            return
        if self.cache:
            message_str = str(message_old)
            message_str_new = str(message_new)
            if message_str in self.cache:
                refresh = self.cache[message_str]
                self.cache.pop(message_str) 
                self.cache[message_str_new] = refresh

    def cache_copy(self, message_old, message_new):
        if self.cache_path:
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()
                message_str = str(message_old)
                message_str_new = str(message_new)
                if message_str in self.cache:
                    self.cache[message_str_new] = self.cache[message_str]
                    self._write_cache_unlocked()
            return
        if self.cache:
            message_str = str(message_old)
            message_str_new = str(message_new)
            if message_str in self.cache:
                self.cache[message_str_new] = self.cache[message_str]

    def request(self, prompt, stop, **kwargs):
        return
    
    def log(self, input, output, **kwargs):
        if "usage" in kwargs and self.cache_path and kwargs['usage'] and isinstance(kwargs['usage'], (list, tuple)) and len(kwargs['usage']) >= 3:
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()
                if self.session_id in self.cache:
                    self.cache[self.session_id][0] += kwargs['usage'][0]
                    self.cache[self.session_id][1] += kwargs['usage'][1]
                    self.cache[self.session_id][2] += kwargs['usage'][2]
                    self.cache[self.session_id][3] += 1
                else:
                    self.cache[self.session_id] = list(kwargs['usage']) + [1]
                self._write_cache_unlocked()
        llm_log(input, output, **kwargs)
        pass


    def get_and_clear_usage(self):
        if self.cache_path:
            with _cache_lock(self.cache_path):
                self.cache = self._read_cache_unlocked()
                if self.session_id in self.cache:
                    usage = self.cache[self.session_id]
                    self.cache.pop(self.session_id)
                    self._write_cache_unlocked()
                    return usage
            return None
        if self.cache and self.session_id in self.cache:
            usage = self.cache[self.session_id]
            self.cache.pop(self.session_id)
            return usage
        return None


class ChatGPT(LLM):
    def __init__(self, name, cache = None, **kwargs) -> None:
        cache_reasoning = kwargs['cache_reasoning'] if 'cache_reasoning' in kwargs else True
        super().__init__(cache, cache_reasoning)
        if '@@@' in name:
            url, name_ = name.split('@@@')
        else:
            url = None
            name_ = name.lower() 
        if name_ in ["gpt-4","gpt4"]:
            self.model_name = "gpt-4-0613"
        else:
            self.model_name = name

        if 'reasoning_model' in kwargs and kwargs['reasoning_model']:
            self.reasoning_model = kwargs['reasoning_model']
        else:
            self.reasoning_model = None # o3-mini-2025-01-31

        if 'force_reasoning' in kwargs:
            self.force_reasoning = kwargs['force_reasoning']
        elif self.model_name.startswith("gpt-5") or self.model_name.startswith("o"):
            self.force_reasoning = True
        else:
            self.force_reasoning = False

        if not self.reasoning_model and self.force_reasoning:
            self.reasoning_model = self.model_name


        if "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
            if 'base_url' in kwargs and kwargs['base_url']:
                self.client = OpenAI(base_url=kwargs['base_url'])
            # elif '.azure.com' in url:
            #     self.client = OpenAI(api_key=os.environ["AZURE_API_KEY"], base_url=url)
            else:
                self.client = OpenAI()
        
        if 'reasoning_effort' in kwargs and kwargs['reasoning_effort']:
            self.reasoning_effort = kwargs['reasoning_effort']
        elif self.model_name.startswith("gpt-5"):
            self.reasoning_effort = "minimal"
        else:
            self.reasoning_effort = "medium"

        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            self.max_tokens = kwargs['max_tokens']
        else:
            self.max_tokens = 2048

        self.use_cache = True


    def generate_message(self, prompt, **kwargs):
        if type(prompt) == list and 'role' in prompt[0]:
            message = prompt
        else:   
            message = [{
                        "role": "user",
                        "content": prompt
                    }]            
        if 'previous_message' in kwargs and kwargs['previous_message']:
            kwargs['previous_message'].extend(message)
            message = kwargs['previous_message']
        return message

    def _chat_completion(self, message, stop, seed, model_name, reasoning_effort, max_tokens, json_format, temperature):
        if self.force_reasoning:
            completion = self.client.chat.completions.create(
                model=model_name,
                reasoning_effort=reasoning_effort,
                messages=message,
                stop = stop,
                seed = seed,
                max_completion_tokens = max_tokens,
                **({"response_format": {"type": "json_object"}} if json_format else {})
            )
        else:
            completion = self.client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                messages=message,
                stop = stop,
                seed = seed,
                max_completion_tokens = max_tokens,
            **({"response_format": {"type": "json_object"}} if json_format else {})
            )
        return completion

    def request(self, prompt, stop, **kwargs):
        message = self.generate_message(prompt, **kwargs)
        
        reasoning_effort = kwargs['reasoning_effort'] if 'reasoning_effort' in kwargs and kwargs['reasoning_effort'] else self.reasoning_effort
        max_tokens = kwargs['max_tokens'] if 'max_tokens' in kwargs and kwargs['max_tokens'] else self.max_tokens
        model_name = self.reasoning_model if (self.reasoning_model and 'reasoning_effort' in kwargs and kwargs['reasoning_effort']) or self.force_reasoning else self.model_name
        json_format = True if 'json_format' in kwargs and kwargs['json_format'] and model_name != "deepseek-reasoner" else False
        temperature = kwargs['temperature'] if 'temperature' in kwargs else 0
        skip_cache = kwargs['skip_cache'] if 'skip_cache' in kwargs and kwargs['skip_cache'] else False
        
        if self.use_cache:
            response, input_tokens, output_tokens = self.from_cache(message, json_format, skip_cache)
            if response:
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
                message.append({"role": "assistant", "content": response})
                return (self.extract_json_string(response), {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens}) if 'json_format' in kwargs and kwargs['json_format'] else (response, {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens})
        
        # try:
        completion = self._chat_completion(message, stop, 8848, model_name, reasoning_effort, max_tokens, json_format, temperature)
        time.sleep(0.5)
        # except:
            # time.sleep(5)
            # completion = self.client.chat.completions.create(
            #     model=model_name,
            #     temperature=temperature,
            #     messages=message,
            #     stop = stop,
            #     seed = 8848,
            #     **({"response_format": {"type": "json_object"}} if json_format else {})
            # )
            # time.sleep(0.5)
        super().log(message, completion.choices[0].message.content, model=completion.model, system_fingerprint = completion.system_fingerprint, usage = [completion.usage.prompt_tokens, completion.usage.completion_tokens, completion.usage.total_tokens])
        # reasoning_content = (getattr(completion.choices[0].message, "model_extra", {}) or {}).get("reasoning_content") or None
        model_extra = getattr(completion.choices[0].message, "model_extra", {}) or {}
        reasoning_content = model_extra.get("reasoning") or model_extra.get("reasoning_content") or None

        self.save_to_cache(message, [completion.choices[0].message.content, completion.usage.prompt_tokens, completion.usage.completion_tokens, reasoning_content])
        
        message.append({"role": "assistant", "content": completion.choices[0].message.content})
        
        self.total_input_tokens += completion.usage.prompt_tokens
        self.total_output_tokens += completion.usage.completion_tokens
        return (self.extract_json_string(completion.choices[0].message.content), {"message": message, "input_tokens": completion.usage.prompt_tokens, "output_tokens": completion.usage.completion_tokens}) if 'json_format' in kwargs and kwargs['json_format'] else (completion.choices[0].message.content, {"message": message, "input_tokens": completion.usage.prompt_tokens, "output_tokens": completion.usage.completion_tokens})
        # return completion.choices[0].message.content, message

    def cache_exchange(self, old_prompt, new_prompt):
        message_old = self.generate_message(old_prompt)
        message_new = self.generate_message(new_prompt)
        super().cache_exchange(message_old, message_new)
            
    def cache_copy(self, old_prompt, new_prompt):
        message_old = self.generate_message(old_prompt)
        message_new = self.generate_message(new_prompt)
        super().cache_copy(message_old, message_new) 

class QianFan(LLM):
    def __init__(self, name, cache = None) -> None:
        import qianfan
        super().__init__(cache)
        self.chat_comp = qianfan.ChatCompletion(model=name)
        # self.chat_comp = qianfan.ChatCompletion(model="ERNIE-Bot-turbo")

    def request(self, prompt, stop, **kwargs):
        message = [{
                    "role": "user",
                    "content": prompt
                }]
        if 'previous_message' in kwargs and kwargs['previous_message']:
            kwargs['previous_message'].extend(message)
            message = kwargs['previous_message']

        response, input_tokens, output_tokens = self.from_cache(message)
        if response:
            message.append({"role": "assistant", "content": response})
            return response, {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens}
        
        try:
            completion = self.chat_comp.do(messages=message, top_p=1, temperature=0.0000001, penalty_score=1.0)
            time.sleep(0.5)
        except:
            time.sleep(5)
            completion = self.chat_comp.do(messages=message, top_p=1, temperature=0.0000001, penalty_score=1.0)
            time.sleep(0.5)
        super().log(message, completion.body['result'], model=self.chat_comp._model, system_fingerprint = completion.body['id'], usage = [completion.body['usage']['prompt_tokens'], completion.body['usage']['completion_tokens'], completion.body['usage']['total_tokens']])
        self.save_to_cache(message, [completion.body['result'], completion.body['usage']['prompt_tokens'], completion.body['usage']['completion_tokens']])
        
        message.append({"role": "assistant", "content": completion.body['result']})

        return completion.body['result'], {"message": message, "input_tokens": completion.body['usage']['prompt_tokens'], "output_tokens": completion.body['usage']['completion_tokens']}




class AWSBedrockLLAMA(LLM):
    def __init__(self, name, cache = None) -> None:
        import boto3
        from botocore.exceptions import ClientError
        super().__init__(cache)
        # name = name.lower()
        if name.lower() == 'llama3.1-405b':
            self.model_name = "meta.llama3-1-405b-instruct-v1:0"
        else:
            self.model_name = name
        session = boto3.Session(
            aws_access_key_id=os.environ["aws_access_key_id"],
            aws_secret_access_key=os.environ["aws_secret_access_key"],
            region_name=os.environ["region_name"]
        )
        # Create a Bedrock Runtime client in the AWS Region you want to use.
        self.client = session.client("bedrock-runtime")

    def request(self, prompt, stop, **kwargs):
        message = [{
                    "role": "user",
                    "content": [{"text": prompt}],
                }]
        
        system_prompts = None
        message_for_cache = message

        if 'previous_message' in kwargs and kwargs['previous_message']:
            kwargs['previous_message'].extend(message)
            message = kwargs['previous_message']
            if message[0]['role'] == 'system':
                system_prompts = [{"text": message[0]['content']}]
                message_for_cache = copy.deepcopy(message)
                del message[0]
            for m in message:
                if type(m['content']) == str:
                    m['content'] = [{"text": m['content']}]
        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            max_tokens = kwargs['max_tokens']
        else:
            max_tokens = 1000

        response, input_tokens, output_tokens = self.from_cache(message_for_cache)
        
        if response:
            message.append({"role": "assistant", "content": [{"text": response}]})
            return (self.extract_json_string(response), {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens}) if 'json_format' in kwargs and kwargs['json_format'] else (response, {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens})
        
        temperature = 0.00001
        topP = 0.9999
        while True:
            try:
                # Send the message to the model, using a basic inference configuration.
                if system_prompts:
                    response = self.client.converse(
                        modelId=self.model_name,
                        messages=message,   system = system_prompts,
                        inferenceConfig={"maxTokens":max_tokens,"temperature":temperature,"topP":topP},
                        additionalModelRequestFields={}
                    )
                else:
                    response = self.client.converse(
                        modelId=self.model_name, messages=message,
                        inferenceConfig={"maxTokens":max_tokens,"temperature":temperature,"topP":topP},additionalModelRequestFields={}
                    )

                # Extract and print the response text.
            except (ClientError, Exception) as e:
                time.sleep(10)
                if system_prompts:
                    response = self.client.converse(
                        modelId=self.model_name,
                        messages=message, system = system_prompts,
                        inferenceConfig={"maxTokens":max_tokens,"temperature":temperature,"topP":topP},
                        additionalModelRequestFields={}
                )
                else:
                    response = self.client.converse(
                        modelId=self.model_name, messages=message,
                        inferenceConfig={"maxTokens":max_tokens,"temperature":temperature,"topP":topP},additionalModelRequestFields={}
                    )
                time.sleep(0.5)
            temperature += 0.333 
            response_text = response["output"]["message"]["content"][0]["text"].strip()
            super().log(message_for_cache, response_text, system_fingerprint = response['stopReason'], usage = [response['usage']['inputTokens'], response['usage']['outputTokens'], response['usage']['totalTokens']])
            
            if 'json_format' in kwargs and kwargs['json_format'] and not self.extract_json_string(response_text):
                assert temperature < 1
            else:
                break        
        self.save_to_cache(message_for_cache, [response_text, response['usage']['inputTokens'], response['usage']['outputTokens']])
        
        message.append({"role": "assistant", "content": [{"text": response_text}]})
        
        return (self.extract_json_string(response_text), {"message": message, "input_tokens": response['usage']['inputTokens'], "output_tokens": response['usage']['outputTokens']}) if 'json_format' in kwargs and kwargs['json_format'] else (response_text, {"message": message, "input_tokens": response['usage']['inputTokens'], "output_tokens": response['usage']['outputTokens']})




class ChatGPTBatch(ChatGPT):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(name, cache, **kwargs)
        batch_folder = 'log/gpt_batch'
        Path(batch_folder).mkdir(parents=True, exist_ok=True) # create `log/gpt_batch` dir if not exist
        batch_cache_path = f'{batch_folder}/gpt_cache.pkl'
        if os.path.exists(batch_cache_path):
            with open(batch_cache_path, 'rb') as file:
                batch_cache = pickle.load(file)
        else:
            batch_cache = OrderedDict()
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        batch_cache[current_time] = {'state':'create', 'cache_path':cache}
        with open(batch_cache_path, 'wb') as file:
            pickle.dump(batch_cache, file)
        self.count = 0
        self.save_jsonl_path = f"log/gpt_batch/{current_time}.jsonl"

    def request(self, prompt, stop, **kwargs):
        message = self.generate_message(prompt, **kwargs)
        reasoning_effort = kwargs['reasoning_effort'] if 'reasoning_effort' in kwargs and kwargs['reasoning_effort'] else self.reasoning_effort
        max_tokens = kwargs['max_tokens'] if 'max_tokens' in kwargs and kwargs['max_tokens'] else self.max_tokens
        model_name = self.reasoning_model if (self.reasoning_model and 'reasoning_effort' in kwargs and kwargs['reasoning_effort']) or self.force_reasoning else self.model_name
        json_format = True if 'json_format' in kwargs and kwargs['json_format'] and model_name != "deepseek-reasoner" else False
        temperature = kwargs['temperature'] if 'temperature' in kwargs else 0
        skip_cache = kwargs['skip_cache'] if 'skip_cache' in kwargs and kwargs['skip_cache'] else False
        response, input_tokens, output_tokens = self.from_cache(message, json_format, skip_cache)
        if response:
            message.append({"role": "assistant", "content": response})
            return response, {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens}
        
        
        example = {}
        example["custom_id"] = "request-{}".format(self.count)
        example["method"] = "POST"
        example["url"] = "/v1/chat/completions"
        body = {}
        body["model"] = model_name
        body["messages"] = message
        if self.force_reasoning:
            body["reasoning_effort"] = reasoning_effort
            body["max_completion_tokens"] = max_tokens
        else:
            body["max_completion_tokens"] = max_tokens
            body["temperature"] = temperature
        if json_format:
            body["response_format"] = {"type": "json_object"}
        example["body"] = body
        self.count += 1

        with open(self.save_jsonl_path, "a") as jsonl_file:
            jsonl_file.write(json.dumps(example) + "\n")

        if 'tag' in kwargs and kwargs['tag']:
            example["yg_tag"] = kwargs['tag']
            with open(self.save_jsonl_path[:-5] + "yg_tag.jsonl", "a") as jsonl_file:
                jsonl_file.write(json.dumps(example) + "\n")
        
        message.append({"role": "assistant", "content": ''})
        
        return '', {"message": message, "input_tokens": None, "output_tokens": None}



class LlamaFactory(LLM):
    def __init__(self, name = "8000", cache = None) -> None:
        super().__init__(cache)
        
        if name.startswith("http"):
            self.client = OpenAI(api_key="0", base_url=name)
            self.model_name = 'unknown'
        else:
            if ":" in name:
                name, port = name.split(":")
            elif name.isdigit():
                port = name
                name = "meta-llama/Meta-Llama-3.1-8B-Instruct"
            else:
                port = "8000"
            self.client = OpenAI(api_key="0", base_url=f"http://0.0.0.0:{port}/v1")
            # example usage for LLaMA Factory inference
            # self.client = OpenAI(api_key="0", base_url=f"https://<Pod_ID>-8000.proxy.runpod.net/v1")
            self.model_name = name


    def request(self, prompt, stop, **kwargs):
        if type(prompt) == list and 'role' in prompt[0]:
            message = prompt
        else:   
            message = [{
                        "role": "user",
                        "content": prompt
                    }]
        if 'previous_message' in kwargs and kwargs['previous_message']:
            kwargs['previous_message'].extend(message)
            message = kwargs['previous_message']
        if 'max_tokens' in kwargs and kwargs['max_tokens']:
            max_tokens = kwargs['max_tokens']
        else:
            max_tokens = 2048
        json_format = True if 'json_format' in kwargs and kwargs['json_format'] else False
        temperature = kwargs['temperature'] if 'temperature' in kwargs else 0

        response, input_tokens, output_tokens = self.from_cache(message, json_format)
        if response:
            message.append({"role": "assistant", "content": response})
            return response, {"message": message, "input_tokens": input_tokens, "output_tokens": output_tokens}
        
        completion = self.client.chat.completions.create(messages=message, model=self.model_name, temperature=temperature, max_tokens=max_tokens)
        super().log(message, completion.choices[0].message.content)
        self.save_to_cache(message, [completion.choices[0].message.content, None, None])

        return (self.extract_json_string(completion.choices[0].message.content), {"message": message, "input_tokens": None, "output_tokens": None}) if 'json_format' in kwargs and kwargs['json_format'] else (completion.choices[0].message.content, {"message": message, "input_tokens": None, "output_tokens": None})


class DeepSeek(ChatGPT):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(name, cache, **kwargs)
        if 'force_reasoning' in kwargs:
            self.force_reasoning = kwargs['force_reasoning']
            self.reasoning_effort = kwargs['reasoning_effort'] if 'reasoning_effort' in kwargs and kwargs['reasoning_effort'] else "medium"
        else:
            self.force_reasoning = False
            self.reasoning_effort = None
        self.model_name = name
        # self.client = OpenAI(api_key=os.environ["DeepSeek_API_KEY"], base_url="https://api.deepseek.com")
        api_key = kwargs.get("api_key") or os.environ.get("DeepSeek_API_KEY")
        base_url = kwargs.get("base_url") or "https://api.deepseek.com"
        self.client = OpenAI( api_key=api_key,  base_url=base_url )

    def _chat_completion(self, message, stop, seed, model_name, reasoning_effort, max_tokens, json_format, temperature):
        if self.force_reasoning:
            completion = self.client.chat.completions.create(
                model=model_name,
                reasoning_effort=reasoning_effort,
                messages=message,
                stop = stop,
                seed = seed,
                max_completion_tokens = max_tokens,
                extra_body={"thinking": {"type": "enabled"}},
                **({"response_format": {"type": "json_object"}} if json_format else {})
            )
        else:
            completion = self.client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                messages=message,
                stop = stop,
                seed = seed,
                max_completion_tokens = max_tokens,
                extra_body={"thinking": {"type": "disabled"}},
            **({"response_format": {"type": "json_object"}} if json_format else {})
            )
        return completion



class vLLM(DeepSeek):
    def __init__(self, name="deepseek-v4-flash", cache=None, **kwargs) -> None:
        kwargs.setdefault("api_key", os.environ.get("VLLM_API_KEY", "EMPTY"))
        if "base_url" not in kwargs:
            kwargs.setdefault("base_url", os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8000/v1"))
        self.token_auto_expand = kwargs.get("token_auto_expand", True)
        super().__init__(name, cache, **kwargs)


    def _chat_completion(self, message, stop, seed, model_name, reasoning_effort, max_tokens, json_format, temperature):
        if self.token_auto_expand:
            space_count = 0
            for m in message:
                if isinstance(m["content"], str):
                    space_count += m["content"].count(" ")
            max_tokens = space_count*2.8 if space_count*2.8 > max_tokens else max_tokens
            for limit in [9888, 15888, 19888, 25888, 29888, 35888, 39888, 45888, 49888, 55888, 59888, 65888, 69888, 75888, 79888, 85888, 89888]:
                if max_tokens <= limit:
                    max_tokens = limit
                    break

        completion = self.client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                messages=message,
                stop = stop,
                seed = seed,
                max_completion_tokens = max_tokens,
                extra_body={
                        "chat_template_kwargs": {
                            "thinking": self.force_reasoning,
                            "reasoning_effort": reasoning_effort,
                        }
                    },
                **({"response_format": {"type": "json_object"}} if json_format else {})
            )
        return completion


class Requesty(ChatGPT):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(name, cache, **kwargs)
        self.model_name = name
        self.client = OpenAI(api_key=os.environ["Requesty_API_KEY"], base_url="https://router.requesty.ai/v1")


class OpenRouter(ChatGPT):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(name, cache, **kwargs)
        self.model_name = name
        self.client = OpenAI(api_key=os.environ["OpenRouter_API_KEY"], base_url="https://openrouter.ai/api/v1")
        self.provider = kwargs['provider'] if 'provider' in kwargs and kwargs['provider'] else []
        if type(self.provider) == str:
            self.provider = [self.provider]
    def _chat_completion(self, message, stop, seed, model_name, reasoning_effort, max_tokens, json_format, temperature):
        completion = self.client.chat.completions.create(
                model=model_name,
                messages=message,
                temperature=temperature,
                stop = stop,
                seed = seed,
                max_tokens = max_tokens,
                extra_body={
                    "provider": {"order": self.provider,"allow_fallbacks": False},
                    "reasoning": {"enabled": self.force_reasoning}}
                )
        return completion



class AzureAI(ChatGPT):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(name, cache, **kwargs)
        self.model_name = name
        self.client = AzureOpenAI(
            azure_endpoint = "https://agcohn-eastus-instance.openai.azure.com/", 
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version="2024-02-01"
            )


class Gemini(LLM):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(cache)
        from google import genai
        self.model_name = name
        if 'reasoning_model' in kwargs and kwargs['reasoning_model']:
            self.reasoning_model = kwargs['reasoning_model']
        else:
            self.reasoning_model = None 
        
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.force_reasoning = False
        
    def request(self, prompt, stop, **kwargs):
        if type(prompt) == list and len(prompt) > 2:
            raise NotImplementedError("Gemini does not support conversation mode.")
        message = str(prompt)
        message_return = [{'role': 'user', 'content': message}]
        
        reasoning_effort = kwargs['reasoning_effort'] if 'reasoning_effort' in kwargs and kwargs['reasoning_effort'] else "medium"
        max_tokens = kwargs['max_tokens'] if 'max_tokens' in kwargs and kwargs['max_tokens'] else 2048
        model_name = self.reasoning_model if (self.reasoning_model and 'reasoning_effort' in kwargs and kwargs['reasoning_effort']) or self.force_reasoning else self.model_name
        json_format = True if 'json_format' in kwargs and kwargs['json_format'] and model_name != "deepseek-reasoner" else False
        temperature = kwargs['temperature'] if 'temperature' in kwargs else 0
        

        response, input_tokens, output_tokens = self.from_cache(message, json_format)
        if response:
            message_return.append({"role": "assistant", "content": response})
            # return response, message
            return (self.extract_json_string(response), {"message": message_return, "input_tokens": input_tokens, "output_tokens": output_tokens}) if 'json_format' in kwargs and kwargs['json_format'] else (response, {"message": message_return, "input_tokens": input_tokens, "output_tokens": output_tokens})

        response = self.client.models.generate_content(
            model=model_name, contents=prompt
        )
        super().log(message_return, response.text, model=self.model_name, usage = [response.usage_metadata.prompt_token_count, (response.usage_metadata.thoughts_token_count or 0)+response.usage_metadata.candidates_token_count, response.usage_metadata.total_token_count])
        self.save_to_cache(message, [response.text, response.usage_metadata.prompt_token_count, (response.usage_metadata.thoughts_token_count or 0)+response.usage_metadata.candidates_token_count])
        
        message_return.append({"role": "assistant", "content": response.text})
        
        return (self.extract_json_string(response.text), {"message": message_return, "input_tokens": response.usage_metadata.prompt_token_count, "output_tokens": (response.usage_metadata.thoughts_token_count or 0)+response.usage_metadata.candidates_token_count}) if 'json_format' in kwargs and kwargs['json_format'] else (response.text, {"message": message_return, "input_tokens": response.usage_metadata.prompt_token_count, "output_tokens": (response.usage_metadata.thoughts_token_count or 0)+response.usage_metadata.candidates_token_count})
        # return completion.choices[0].message.content, message


class Requesty_Gemini(Gemini):
    def __init__(self, name, cache = None, **kwargs) -> None:
        super().__init__(name, cache, **kwargs)
        name_ = name.lower()
        self.model_name = name
        self.client = OpenAI(api_key=os.environ["Requesty_API_KEY"], base_url="https://router.requesty.ai/v1")


def submit_ChatGPTBatch():
    batch_cache_path = 'log/gpt_batch/gpt_cache.pkl'
    if not os.path.exists(batch_cache_path):
        return
    with open(batch_cache_path, 'rb') as file:
        batch_cache = pickle.load(file)

    target_ids = {}
    client = OpenAI()
    for bkey in list(batch_cache.keys()):  
        jsonl_path = f"log/gpt_batch/{bkey}.jsonl"
        if not os.path.exists(jsonl_path):
            batch_cache.pop(bkey)
            with open(batch_cache_path, 'wb') as file:
                pickle.dump(batch_cache, file)
            continue
        if batch_cache[bkey]['state'] == 'finished':
            continue
        elif batch_cache[bkey]['state'] == 'submited':
            target_ids[batch_cache[bkey]['job_id']] = bkey
            continue

        batch_input_file = client.files.create(
            file=open(jsonl_path, "rb"),
            purpose="batch"
        )

        batch_input_file_id = batch_input_file.id
        batch_cache[bkey]['batch_input_file_id'] = batch_input_file_id
        batch_job = client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
            "description": bkey
            }
        )
        print(f'Job {jsonl_path} has been submitted.')
        batch_cache[bkey]['state'] = 'submited'
        batch_cache[bkey]['job_id'] = batch_job.id
        target_ids[batch_job.id] = bkey
        with open(batch_cache_path, 'wb') as file:
            pickle.dump(batch_cache, file)


    while target_ids:
        output_file_id = None
        obj_id = None
        bath_obj = client.batches.list(limit=10)
        for obj in bath_obj.data:
            if obj.id in target_ids.keys():
                obj_id = obj.id
                print(obj)
                if obj.output_file_id:
                    output_file_id = obj.output_file_id
                    break
                elif obj.error_file_id:
                    raise Exception("The job {0} failed.\n{1}".format(target_ids[obj.id], client.files.content(obj.error_file_id).text))
                elif obj.completed_at:
                    raise Exception("The job {0} failed without error message.".format(target_ids[obj.id]))

        if not output_file_id:  
            assert obj_id
            print(target_ids)
            print(f"GPT is busy, waiting for {90} seconds before checking again...")
            print()
            time.sleep(90)
        else:
            result = client.files.content(output_file_id)
            results = result.text.strip().split('\n')
            bkey = target_ids[obj.id]
            outputs = []
            print(f"Job {bkey} has been finished.")
            if os.path.exists(f"log/gpt_batch/{bkey}.yg_tag.jsonl"):
                jsonl_path = f"log/gpt_batch/{bkey}.yg_tag.jsonl"
                os.remove(f"log/gpt_batch/{bkey}.jsonl")
            else:
                jsonl_path = f"log/gpt_batch/{bkey}.jsonl"
            usage_data = {"prompt_tokens": 0, "completion_tokens": 0}
            file_data = {}
            with open(jsonl_path, "r") as file:
                for line in file:
                    out = json.loads(line.strip())
                    if 'custom_id' in out:  # Make sure custom_id exist
                        file_data[out['custom_id']] = out
            outputs = []
            for r in results:
                response = json.loads(r)
                response_id = response.get('custom_id')  # take response ID
                if response_id in file_data:  # Make sure ID exist
                    out = file_data[response_id]  # find out
                    out["predict"] = response['response']['body']['choices'][0]['message']['content']
                    usage_data["prompt_tokens"] += response['response']['body']['usage']['prompt_tokens']
                    usage_data["completion_tokens"] += response['response']['body']['usage']['completion_tokens']
                    out["usage"] = {'prompt_tokens': response['response']['body']['usage']['prompt_tokens'], 'completion_tokens': response['response']['body']['usage']['completion_tokens']}
                    outputs.append(out)
                    
            print(usage_data)
            with open(f"log/gpt_batch/{bkey}.json", "w") as file:
                json.dump(outputs, file)

            
            # Update cache
            llm_cache_path = batch_cache[bkey]['cache_path']
            if llm_cache_path:
                if os.path.exists(llm_cache_path):
                    with open(llm_cache_path, 'rb') as file:
                        llm_cache = pickle.load(file)
                else:
                    llm_cache = OrderedDict()
                
                for out in outputs:
                    llm_cache[str(out["body"]["messages"])] = [out["predict"], out["usage"]["prompt_tokens"], out["usage"]["completion_tokens"]]

                with open(llm_cache_path, 'wb') as file:
                    pickle.dump(llm_cache, file)
            
            target_ids.pop(obj.id)
            batch_cache.pop(bkey)
            with open(batch_cache_path, 'wb') as file:
                pickle.dump(batch_cache, file)



if __name__ == '__main__':
    from ALL_KEYS import *
    # PYTHONPATH=/Users/yujiangan/Documents/python/CORDIAL-AI  python /Users/yujiangan/Documents/python/CORDIAL-AI/utils/llm.py
    submit_ChatGPTBatch()
