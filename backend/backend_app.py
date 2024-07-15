from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def generate_new_id():
    if POSTS:
        return max(post['id'] for post in POSTS) + 1
    else:
        return 1


@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Extract query parameters for sorting
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Validate and sort
    if sort_field:
        if sort_field not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field. Must be 'title' or "
                                     "'content'."}), 400
        if sort_direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid sort direction. Must be 'asc' "
                                     "or 'desc'."}), 400
        reverse = sort_direction == 'desc'
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_field],
                              reverse=reverse)
    else:
        sorted_posts = POSTS

    # Implement pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = sorted_posts[start:end]

    return jsonify(paginated_posts)



@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Validate input
    if not data or 'title' not in data or 'content' not in data:
        missing_fields = []
        if 'title' not in data:
            missing_fields.append('title')
        if 'content' not in data:
            missing_fields.append('content')
        return jsonify(
            {"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Generate new ID and create new post
    new_post_id = generate_new_id()
    new_post = {
        "id": new_post_id,
        "title": data['title'],
        "content": data['content']
    }
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = next((post for post in POSTS if post['id'] == id), None)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    POSTS.remove(post)
    return jsonify(
        {"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    post = next((post for post in POSTS if post['id'] == id), None)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    # Update title and content if provided, otherwise keep current values
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title')
    content_query = request.args.get('content')

    filtered_posts = POSTS
    if title_query:
        filtered_posts = [post for post in filtered_posts if
                          title_query.lower() in post['title'].lower()]
    if content_query:
        filtered_posts = [post for post in filtered_posts if
                          content_query.lower() in post['content'].lower()]

    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
