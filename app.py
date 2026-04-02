from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)

app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'Aviral@123'   # ← change to YOUR password
app.config['MYSQL_DB']       = 'school_db'

mysql = MySQL(app)


def validate_student(data):
    errors = []
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors.append('name is required and must be at least 2 characters')
    if not data.get('email') or '@' not in data['email']:
        errors.append('a valid email is required')
    if not data.get('age') or not str(data['age']).isdigit() or int(data['age']) < 1 or int(data['age']) > 100:
        errors.append('age must be a number between 1 and 100')
    if not data.get('course') or len(data['course'].strip()) < 2:
        errors.append('course is required')
    return errors


@app.route('/')
def home():
    return jsonify({
        'message': 'Student CRUD API is running!',
        'endpoints': {
            'POST   /students':      'Create student',
            'GET    /students':      'Get all students',
            'GET    /students/<id>': 'Get student by ID',
            'PUT    /students/<id>': 'Update student by ID',
            'DELETE /students/<id>': 'Delete student by ID'
        }
    }), 200


@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    errors = validate_student(data)
    if errors:
        return jsonify({'errors': errors}), 400

    name   = data['name'].strip()
    email  = data['email'].strip()
    age    = int(data['age'])
    course = data['course'].strip()

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO student (name, email, age, course) VALUES (%s, %s, %s, %s)",
            (name, email, age, course)
        )
        mysql.connection.commit()
        new_id = cur.lastrowid
        cur.close()
        return jsonify({
            'message': 'Student created successfully',
            'student': {'id': new_id, 'name': name, 'email': email, 'age': age, 'course': course}
        }), 201
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student")
        rows = cur.fetchall()
        cur.close()
        students = [
            {'id': r[0], 'name': r[1], 'email': r[2], 'age': r[3], 'course': r[4]}
            for r in rows
        ]
        return jsonify({'students': students, 'count': len(students)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
        row = cur.fetchone()
        cur.close()
        if row is None:
            return jsonify({'error': f'Student with id {student_id} not found'}), 404
        return jsonify({'student': {
            'id': row[0], 'name': row[1], 'email': row[2], 'age': row[3], 'course': row[4]
        }}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    errors = validate_student(data)
    if errors:
        return jsonify({'errors': errors}), 400

    name   = data['name'].strip()
    email  = data['email'].strip()
    age    = int(data['age'])
    course = data['course'].strip()

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM student WHERE id = %s", (student_id,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({'error': f'Student with id {student_id} not found'}), 404
        cur.execute(
            "UPDATE student SET name=%s, email=%s, age=%s, course=%s WHERE id=%s",
            (name, email, age, course, student_id)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({
            'message': 'Student updated successfully',
            'student': {'id': student_id, 'name': name, 'email': email, 'age': age, 'course': course}
        }), 200
    except MySQLdb.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM student WHERE id = %s", (student_id,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({'error': f'Student with id {student_id} not found'}), 404
        cur.execute("DELETE FROM student WHERE id = %s", (student_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': f'Student with id {student_id} deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)