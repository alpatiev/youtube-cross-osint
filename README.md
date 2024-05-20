# README

## About
I finally found a good source of unique text data to train LLMs.
So I'm gonna try to play with that a little.

## Installation 
A) Normal
1. Create a virtual environment:
    ```sh
    python -m venv env
    ```
2. Activate the virtual environment:
    - On Windows:
        ```sh
        .\env\Scripts\activate
        ```
    - On Unix:
        ```sh
        source env/bin/activate
        ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

B) For extremely lazy people:

    ```sh
    bash lazy.sh
    ```

And to launch use `cmd/windows` + `b`, change .tasks.json as you need.
    
## Usage
All results will be saved in `data` folder:

1. Set the API key (-k/--api-key):
    ```sh
    python scripts/app.py -k YOUR_API_KEY
    ```

2. Scrape videos without comments (-s/--short):
    ```sh
    python scripts/app.py -s -u CHANNEL_URL
    ```

3. Scrape videos with comments (-f/--full):
    ```sh
    python scripts/app.py -f -u CHANNEL_URL
    ```

## To-Do
- Make multi-core
- Save to database instead of JSON
- Make modular

## License
MIT 
