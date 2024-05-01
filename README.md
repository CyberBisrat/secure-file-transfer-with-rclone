# secure-file-transfer-with-rclone


This API provides endpoints for transfering encrypted files using the rclone. It offers functionality for uploading encrypted data, deleting files, and listing synced files in remote location. 

## Authentication

All endpoints require a valid token to be passed in the `Authorization` header. The token must be provided in the format: `Bearer <your_token>`. The token is verified against the one set in the environment variable `RCLONE_API_BEARER_TOKEN`.

## Endpoints

### 1. Upload Encrypted Data

- **Endpoint:** `/upload_encrypted`
- **Method:** POST
- **Authentication Required:** Yes
- **Request Body:**
    ```json
    {
        "source": "/temp/example/example.txt",
        "destination": "/example/example.txt"
    }
    ```
- **Description:** Uploads encrypted data from a specified source to the destination path.

### 2. Delete File

- **Endpoint:** `/delete_file`
- **Method:** POST
- **Authentication Required:** Yes
- **Request Body:**
    ```json
    {
        "remote_path": "/example/example.txt"
    }
    ```
- **Description:** Deletes a file located at the specified remote path.

### 3. List Encrypted Files

- **Endpoint:** `/list_encrypted_files`
- **Method:** GET
- **Authentication Required:** Yes
- **Description:** Lists all synced files that are encrypted.

## Responses

- **Success Response (200):**
    ```json
    {
        "message": "File deleted successfully."
    }
    ```
- **Error Response (4xx, 5xx):**
    ```json
    {
        "error": "Error message"
    }
    ```

## Error Handling

- If an error occurs during the execution of an endpoint, an appropriate error message along with the HTTP status code is returned.



## Documentation
https://rclone.org/docs/#config-config-file

https://rclone.org/commands/

https://rclone.org/docs/
