from app.database import db
from datetime import datetime

class BPAnalytics(db.Model):
    """Model for storing blood pressure analytics data."""
    __tablename__ = 'bp_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Time range of the analysis
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Aggregated statistics
    avg_systolic = db.Column(db.Float, nullable=True)
    avg_diastolic = db.Column(db.Float, nullable=True)
    max_systolic = db.Column(db.Integer, nullable=True)
    max_diastolic = db.Column(db.Integer, nullable=True)
    min_systolic = db.Column(db.Integer, nullable=True)
    min_diastolic = db.Column(db.Integer, nullable=True)
    reading_count = db.Column(db.Integer, nullable=False, default=0)
    abnormal_reading_count = db.Column(db.Integer, nullable=False, default=0)
    
    # Trend analysis
    trend_direction = db.Column(db.String(20), nullable=True)  # "improving", "worsening", "stable"
    trend_details = db.Column(db.Text, nullable=True)
    
    # Report generation tracking
    pdf_report_path = db.Column(db.String(255), nullable=True)
    excel_report_path = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('bp_analytics', lazy=True))
    
    def __repr__(self):
        return f'<BPAnalytics {self.id} for user {self.user_id}: {self.start_date} to {self.end_date}>'
    
    @property
    def serialize(self):
        """Return data in serializable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'avg_systolic': self.avg_systolic,
            'avg_diastolic': self.avg_diastolic,
            'max_systolic': self.max_systolic,
            'max_diastolic': self.max_diastolic,
            'min_systolic': self.min_systolic,
            'min_diastolic': self.min_diastolic,
            'reading_count': self.reading_count,
            'abnormal_reading_count': self.abnormal_reading_count,
            'trend_direction': self.trend_direction,
            'trend_details': self.trend_details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 