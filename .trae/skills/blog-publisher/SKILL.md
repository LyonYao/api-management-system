---
name: "blog-publisher"
description: "Publishes blog posts to the API. Invoke when user wants to publish content to the blog API, including title, content, categories, and tags."
---

# Blog Publisher

This skill allows you to publish blog posts to the API at `https://api.ilyon.cn/v1/api/blog/posts`.

## How It Works

1. **Login**: First, the skill logs in to the API using the provided credentials to obtain an authentication token.
2. **Publish**: Then, it uses the obtained token to publish the blog post with the specified title, content, categories, and tags.

## Usage

When the user wants to publish content to the blog API, use this skill to:

1. Login with the provided credentials
2. Prepare the blog post data
3. Send the request to the API with the authentication token
4. Return the response from the API

## Required Parameters

### For Login
- `username`: The username for authentication (default: "admin")
- `password`: The password for authentication (default: "GHSG6RsC9FF2OIop")

### For Blog Post
- `title`: The title of the blog post (can be AI-generated)
- `content`: The content of the blog post (HTML format, can be AI-generated and edited with tinyMCE)
- `categories`: An array of categories for the blog post
- `tags`: An array of tags for the blog post (default: ["ai", "skill", "trae"])
- `published`: Whether the post should be published (default: true)

## API Endpoints

- **Login**: `https://api.ilyon.cn/v1/api/blog/auth/login` (POST)
- **Publish Post**: `https://api.ilyon.cn/v1/api/blog/posts` (POST)

## Authentication

The authentication token obtained from the login response must be included in the `Authorization` header as a Bearer token for the publish request.

## Example Workflow

1. User provides content to be published as a blog post
2. Use this skill to:
   - Login to the API to get a token
   - Format the content with title, categories, and tags
   - Send the request to publish the post
   - Return the API response to the user

## Response Format

The API returns a response with the created post details, including:
- `message`: Success message
- `post`: Object containing the post details (id, title, content, categories, tags, etc.)