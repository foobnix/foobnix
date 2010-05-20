package com.foobnix.vk;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.HttpResponse;
import org.apache.http.NameValuePair;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.utils.URLEncodedUtils;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HTTP;
import org.apache.http.protocol.HttpContext;
import org.apache.http.util.EntityUtils;
import org.codehaus.jackson.map.ObjectMapper;

public class VKlogin {
    private static final String DEFAULT_LOGIN_URL = "http://vkontakte.ru/login.php";
    private final String login;
    private final String password;

    public VKlogin(String login, String password) {
        this.login = login;
        this.password = password;
    }

    public LoginResult getLoginResult() throws ClientProtocolException, IOException {

        List<NameValuePair> params = new ArrayList<NameValuePair>();
        params.add(new BasicNameValuePair("noredirect", "1"));
        params.add(new BasicNameValuePair("email", login));
        params.add(new BasicNameValuePair("pass", password));

        HttpPost post = new HttpPost(DEFAULT_LOGIN_URL);
        post.setEntity(new UrlEncodedFormEntity(params, HTTP.UTF_8));
        post.addHeader("X-Requested-With", "XMLHttpRequest");
        HttpClient httpClient = new DefaultHttpClient();
        HttpContext httpContext = new BasicHttpContext();
        HttpResponse resp = httpClient.execute(post, httpContext);

        String url = DEFAULT_LOGIN_URL + URLEncodedUtils.format(params, "UTF-8");
        System.out.println(url);

        String respContent = EntityUtils.toString(resp.getEntity());
        System.out.println(respContent);

        ObjectMapper objectMapper = new ObjectMapper();
        LoginResult loginResult = objectMapper.readValue(respContent, LoginResult.class);
        System.out.println(loginResult.getId());
        System.out.println(loginResult.getSid());

        List<NameValuePair> par = new ArrayList<NameValuePair>();
        par.add(new BasicNameValuePair("c[q]", "Madonna"));
        par.add(new BasicNameValuePair("c[section]", "audio"));

        HttpPost post1 = new HttpPost(
                "http://vkontakte.ru/gsearch.php?section=audio&q=vasya#c[q]=some%20id&c[section]=audio");
        post1.setEntity(new UrlEncodedFormEntity(par, HTTP.UTF_8));
        post1.addHeader("X-Requested-With", "XMLHttpRequest");

        HttpResponse execute = httpClient.execute(post1, httpContext);
        String respContent1 = EntityUtils.toString(execute.getEntity());

        FileWriter file = new FileWriter("out.txt");
        String replace = respContent1.replace("\\n", "\n");
        file.write(replace);
        file.close();
        System.out.println(replace);

        return loginResult;
    }
}
