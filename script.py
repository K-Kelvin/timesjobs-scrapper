from bs4 import BeautifulSoup
from os import path
from datetime import datetime
import requests
import csv
import shutil

search_param = "python"
url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={search_param}&txtLocation="
all_jobs = []


def download_image(img_url, filename="img.jpg"):
    response = requests.get(img_url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
        return True
    else:
        return False


def find_jobs(print_to_cmd=False):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    job_tags = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")
    for job in job_tags:
        category = job.header.h2.text.strip()
        company = job.find(
            'h3', class_="joblist-comp-name").text.strip().replace("\n", " ").replace("\r", "")

        detail_lis = job.find(
            'ul', class_="top-jd-dtl clearfix").find_all('li')
        years_of_experience = detail_lis[0].contents[1]
        job_location = detail_lis[1].span.text if detail_lis[1].span else detail_lis[1].text
        desc_n_skills = job.find(
            'ul', class_="list-job-dtl clearfix").find_all('li')
        description = desc_n_skills[0].contents[2].replace(
            R"\r\n", " ").strip()
        desc_link = job.header.h2.a['href']
        skills = job.find(
            'span', class_="srp-skills").text.strip().replace("  ,", ",").replace("  ", " ")
        posted = job.find('span', class_="sim-posted").text.strip()
        days_ago = " ".join(posted.split(" ")[1:]).replace(
            "\n", " ").replace("\r", "")

        txt = f'''
        Category: {category} 
        Company: {company}
        Years of experience: {years_of_experience}
        Job location: {job_location}
        Description: {description}
        More Info: {desc_link}
        Skills: {skills}
        Posted: {days_ago}

        '''
        all_jobs.append({
            "category": category,
            "company": company,
            "years_of_experience": years_of_experience,
            "job_location": job_location,
            "description": description,
            "more_info": desc_link,
            "skills": skills,
            "posted": days_ago
        })
        if print_to_cmd:
            print(txt)


def save_as_csv(jobs, filepath, mode):
    with open(filepath, mode, encoding="utf-8", newline="") as csv_file:
        fieldnames = all_jobs[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)


def save_as_txt(jobs, filepath, mode):
    with open(filepath, mode, encoding="utf-8") as file:
        for job in jobs:
            file.write(f"Category: {job['category']}\n")
            file.write(f"Company: {job['company']}\n")
            file.write(f"Years of experience: {job['years_of_experience']}\n")
            file.write(f"Job location: {job['job_location']}\n")
            file.write(f"Description: {job['description']}\n")
            file.write(f"More Info: {job['more_info']}\n")
            file.write(f"Skills: {job['skills']}\n")
            file.write(f"Posted: {job['posted']}\n")
            file.write("\n")


def save_to_file(jobs, file_type="txt", mode="w"):
    if mode not in ['w', 'a']:
        print("Only overwriting(w) and appending(a) to file allowed!")
        exit()
    if file_type not in ['txt', 'csv']:
        print("Only csv and txt modes allowed!")
        exit()
    mode += "+"
    date = datetime.now().strftime("%d-%b-%Y")
    filepath = path.join("jobs", f"jobs_{search_param}_{date}.{file_type}")
    if (file_type == 'txt'):
        save_as_txt(jobs, filepath, mode)
    elif (file_type == 'csv'):
        save_as_csv(jobs, filepath, mode)
    print(f"Successfully written to {filepath}")


if __name__ == "__main__":
    print("Scrape Job Data from www.timesjobs.com\n")
    choice = 'n'  # input("Print to cmd? (y/n): ").strip().lower()
    filetype = input("Enter filetype: (csv/txt): ").strip().lower()
    if choice in ['y', 'n']:
        print_to_cmd = True if choice == "y" else False
        find_jobs(print_to_cmd)
        if not print_to_cmd:
            save_to_file(all_jobs, file_type=filetype)
    else:
        print('Invalid choice, input either y or n')
        exit()
