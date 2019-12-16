import axios from 'axios';
import React, { useState } from 'react';
import Avatar from '@material-ui/core/Avatar';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import Container from '@material-ui/core/Container';
import CssBaseline from '@material-ui/core/CssBaseline';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Grid from '@material-ui/core/Grid';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import Link from '@material-ui/core/Link';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';


const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
}));


const Login = () => {
  const classes = useStyles();
  const [username, saveUsername] = useState('');
  const [password, savePassword] = useState('');
  const [remember, saveRemember] = useState(false);
  const [token, saveToken] = useState('');

  const handleRemember = () => {
    saveRemember(!remember);
  }

  const disabled = !(username && password && /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(username));

  const SubmitLogin = async e => {
    e.preventDefault();
    const payload = {email: username, password:password};
    const res = await axios.post('http://localhost:8000/api/user/token/', payload);
    saveToken(res.data.token);
  }

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <Avatar className={classes.avatar}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography component="h1" variant="h5">
          Log In
        </Typography>
        <form className={classes.form} onSubmit={SubmitLogin} noValidate>
          <TextField
            variant="outlined" margin="normal" required type="email"
            fullWidth id="username" label="Username" name="username"
            value={username} autoComplete="username" autoFocus
            onChange={ e => saveUsername(e.target.value) } />
          <TextField
            variant="outlined" margin="normal" required fullWidth
            name="password" label="Password" type="password" id="password"
            value={password} autoComplete="current-password"
            onChange={ e => savePassword(e.target.value) } />
          <FormControlLabel
            control={<Checkbox
                      value={remember} 
                      onChange={ handleRemember }
                      color="primary" />}
            label="Remember me" />
          <Button
            type="submit" fullWidth variant="contained" color="primary"
            className={classes.submit} disabled={disabled}>
            Sign In
          </Button>
          <Grid container>
            <Grid item xs>
              <Link href="#" variant="body2">
                Forgot password?
              </Link>
            </Grid>
          </Grid>
        </form>
      </div>
    </Container>
  );
}


export default Login;