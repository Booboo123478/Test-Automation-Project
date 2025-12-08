import axios from "axios";
import { endpoint } from "./constants";

export const authAxios = axios.create({
  baseURL: endpoint
});

// Ajouter un intercepteur pour inclure le token d'authentification dans les en-têtes - MA
authAxios.interceptors.request.use(
  config => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
