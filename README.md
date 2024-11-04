

# MongoDB Handler Project

## Overview

This project provides a simple API for interacting with a MongoDB database. The API allows for reading data from the database using a JSON-based query language.

## Features

- Supports reading data from a MongoDB database using a JSON-based query language
- Allows for querying data based on various fields, including `_id`, `owner`, and `shopName`
- Returns data in a JSON format

## API Endpoints

- `/data`: Handles GET requests for reading data from the database

## Query Language

The query language used in this project is a JSON-based language that allows for querying data based on various fields. The query language supports the following operators:

- `$oid`: Used to query data based on an ObjectId field
- `$eq`: Used to query data based on an exact match

## Example Queries

- Querying data based on an `_id` field:

    ```json
    {
        "operation": {
            "type": "read",
            "collection_name": "shops",
            "query": {"_id": {"$oid": "6680398b31d18d7b1569607a"}},
            "bulk": true
        }
    }
    ```

- Querying data based on an `owner` field:

    ```json
    {
        "operation": {
            "type": "read",
            "collection_name": "shops",
            "query": {"owner": {"$oid": "6625d389abc4d75c3101eb5a"}},
            "bulk": true
        }
    }
    ```

- Querying data based on a `shopName` field:

    ```json
    {
        "operation": {
            "type": "read",
            "collection_name": "shops",
            "query": {"shopName": "Golden Gallery"},
            "bulk": true
        }
    }
    ```

## Environment Variables

To run the project, you need to set the following environment variable:

- `MONGO_URL`: The URL of your MongoDB instance. For example: `mongodb://localhost:27017/`

You can set the environment variable in your terminal or command prompt:

```bash
export MONGO_URL=mongodb://localhost:27017/
```

Alternatively, you can include the environment variable in a `.env` file in the root of your project:

```makefile
MONGO_URL=mongodb://localhost:27017/
```

## Running the Project

To run the project, simply execute the following command:

```bash
curl -X GET \
  -H "Content-Type: application/json" \
  -d '{...}' \
  http://127.0.0.1:5000/data
```

Replace `{...}` with the desired query.

## Contributing

Contributions to this project are welcome. To contribute, simply fork the repository, make the desired changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.