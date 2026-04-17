from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(_error):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(409)
    def conflict(_error):
        return jsonify({"error": "Conflict"}), 409

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Internal server error"}), 500
