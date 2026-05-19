from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange


class RegisterForm(FlaskForm):
    full_name = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField("Conferma password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrati")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Accedi")


class PlantForm(FlaskForm):
    name = StringField("Nome impianto", validators=[DataRequired(), Length(max=120)])
    plant_type = SelectField(
        "Tipologia",
        choices=[
            ("fotovoltaico", "Fotovoltaico"),
            ("eolico", "Eolico"),
            ("cogenerazione", "Cogenerazione"),
        ],
        validators=[DataRequired()],
    )
    installed_kw = FloatField("kW installati", validators=[DataRequired(), NumberRange(min=0.1, max=100000)])
    install_date = DateField("Data installazione", validators=[DataRequired()])
    submit = SubmitField("Salva impianto")


class VehicleForm(FlaskForm):
    model = StringField("Modello", validators=[DataRequired(), Length(max=120)])
    battery_kwh = FloatField("Capacità batteria (kWh)", validators=[DataRequired(), NumberRange(min=0.1, max=1000)])
    submit = SubmitField("Salva veicolo")


class MeasurementForm(FlaskForm):
    day = DateField("Giorno", validators=[DataRequired()])
    production_kwh = FloatField("Produzione (kWh)", validators=[DataRequired(), NumberRange(min=0, max=100000)])
    consumption_kwh = FloatField("Consumo (kWh)", validators=[DataRequired(), NumberRange(min=0, max=100000)])
    km_travelled = FloatField("Km percorsi", validators=[DataRequired(), NumberRange(min=0, max=10000)])
    submit = SubmitField("Registra misurazione")
