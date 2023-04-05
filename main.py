from flask import Flask, abort, request
import sys
from flask_restful import Api, Resource, inputs, reqparse
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
api = Api(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(128))
    date = db.Column(db.Date)

    def serialize(self):
        return {'id': self.id,
                'event': self.event_name,
                'date': self.date.strftime('%Y-%m-%d')}


db.create_all()

create_event_parser = reqparse.RequestParser()

create_event_parser.add_argument(
    'date',
    type=inputs.date,
    help='The event date with the correct format is required! ' +
         'The correct format is YYYY-MM-DD!',
    required=True)

create_event_parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True)


class TodayEventResource(Resource):
    def get(self):
        events = Event.query.filter(
            Event.date == datetime.today().strftime('%Y-%m-%d')).all()
        return [event.serialize() for event in events]


class EventResource(Resource):
    def get(self):
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time and end_time:
            events = Event.query.filter(
                Event.date >= start_time, Event.date <= end_time).all()
        else:
            events = Event.query.all()
        return [event.serialize() for event in events]

    def post(self):
        args = create_event_parser.parse_args()

        event = Event(event_name=args['event'], date=args['date'])
        db.session.add(event)
        db.session.commit()

        return {'message': 'The event has been added!',
                'event': args['event'],
                'date': args['date'].strftime('%Y-%m-%d')}


class EventByIdResource(Resource):
    def get(self, event_id):

        event = Event.query.get(event_id)
        if not event:
            return abort(404, "The event doesn't exist!")
        return event.serialize()

    def delete(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            return abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {'message': 'The event has been deleted!'}


api.add_resource(TodayEventResource, '/event/today')
api.add_resource(EventByIdResource, '/event/<int:event_id>')
api.add_resource(EventResource, '/event')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
