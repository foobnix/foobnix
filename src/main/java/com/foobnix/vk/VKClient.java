package com.foobnix.vk;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.lang.StringUtils;
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
import org.apache.log4j.Logger;
import org.codehaus.jackson.JsonParseException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;

public class VKClient {
    private final static Logger LOG = Logger.getLogger(VKClient.class);
    private final HttpClient httpClient = new DefaultHttpClient();
    private final HttpContext httpContext = new BasicHttpContext();

    private static final String DEFAULT_LOGIN_URL = "http://vkontakte.ru/login.php";
    private final String login;
    private final String password;

    public VKClient(String login, String password) {
        LOG.info("begin");
        this.login = login;
        this.password = password;
    }

    public String getResponseSearch(String query) throws ClientProtocolException, IOException {

        LoginResult loginResult = validateLogin();

        if (StringUtils.isNotEmpty(loginResult.getError())) {
            new VKExeption("Authorization not success" + loginResult.getError());
        }
        String searchResponce = processSearch(query);
        return searchResponce.replace("\\n", "\n");
    }

    private String processSearch(String query) throws UnsupportedEncodingException, IOException,
            ClientProtocolException {
        List<NameValuePair> par = new ArrayList<NameValuePair>();
        par.add(new BasicNameValuePair("c[q]", query));
        par.add(new BasicNameValuePair("c[section]", "audio"));

        HttpPost post = new HttpPost(
                "http://vkontakte.ru/gsearch.php?section=audio&q=vasya#c[q]=some%20id&c[section]=audio");
        post.setEntity(new UrlEncodedFormEntity(par, HTTP.UTF_8));
        post.addHeader("X-Requested-With", "XMLHttpRequest");

        HttpResponse execute = httpClient.execute(post, httpContext);
        String result = EntityUtils.toString(execute.getEntity());
        return result;
    }

    private LoginResult validateLogin() throws UnsupportedEncodingException, IOException, ClientProtocolException,
            JsonParseException, JsonMappingException {
        List<NameValuePair> params = new ArrayList<NameValuePair>();
        params.add(new BasicNameValuePair("noredirect", "1"));
        params.add(new BasicNameValuePair("email", login));
        params.add(new BasicNameValuePair("pass", password));

        HttpPost post = new HttpPost(DEFAULT_LOGIN_URL);
        post.setEntity(new UrlEncodedFormEntity(params, HTTP.UTF_8));
        post.addHeader("X-Requested-With", "XMLHttpRequest");
        HttpResponse resp = httpClient.execute(post, httpContext);

        String url = DEFAULT_LOGIN_URL + URLEncodedUtils.format(params, "UTF-8");
        LOG.debug("Connection url" + url);

        String respContent = EntityUtils.toString(resp.getEntity());

        ObjectMapper objectMapper = new ObjectMapper();
        LoginResult loginResult = objectMapper.readValue(respContent, LoginResult.class);
        return loginResult;
    }

    public List<VkSong> search(String query) {
        List<VkSong> result = new ArrayList<VkSong>();

        String responseSearch = "";
        String songSource = "return operate\\(([0-9]*),([0-9]*),([0-9]*),'([a-z0-9]*)',([0-9]*)\\)";
        try {
            responseSearch = getResponseSearch(query);
        } catch (IOException e) {
            LOG.error("Search error", e);
        }
        Pattern pattern = Pattern.compile(songSource);
        Matcher matcher = pattern.matcher(responseSearch);

        while (matcher.find()) {
            String id = matcher.group(1);
            String server = matcher.group(2);
            String folder = matcher.group(3);
            String fileName = matcher.group(4);

            String path = getPath(server, folder, fileName);
            LOG.debug(path);
            result.add(new VkSong(id, path));
        }

        return result;
    }

    private static String getPath(String server, String folder, String fileName) {
        return "http://cs" + server + ".vkontakte.ru/u" + folder + "/audio/" + fileName + ".mp3";
    }

    public static void main(String[] args) throws ClientProtocolException, IOException {
        VKClient client = new VKClient("qax@bigmir.net", "foobnix");
        String responseSearch = client.getResponseSearch("Madonna - Frozen");
        System.out.println(responseSearch);

        String reg_all = "([^<>]*)";

        String info = "return operate\\(([0-9]*),([0-9]*),([0-9]*),'([a-z0-9]*)',([0-9]*)\\)";
        String artist = "title([0-9]*)\\\\\">" + reg_all + "<";
        String title = "performer([0-9]*)\\\\\">" + reg_all + "<";
        String time = "duration\\\\\">" + reg_all + "<" + reg_all + "<";

        // Compile and use regular expression
        Pattern pattern = Pattern.compile(info, Pattern.UNIX_LINES);
        Matcher matcher = pattern.matcher(responseSearch);
        LOG.debug("MATCH");
        while (matcher.find()) {
            for (int i = 0; i <= matcher.groupCount(); i++) {
                String groupStr = matcher.group(i);
                LOG.debug(groupStr);
            }
            String id_id = matcher.group(1);
            String id_server = matcher.group(2);
            String id_folder = matcher.group(3);
            String id_file = matcher.group(4);

            LOG.debug(getPath(id_server, id_folder, id_file));
        }

    }
}
